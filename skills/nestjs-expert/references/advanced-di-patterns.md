# Advanced Dependency Injection Patterns

Deep-dive reference for NestJS dependency injection. Load when dealing with DI errors, custom providers, dynamic module configuration, or injection scope issues.

---

## Custom Provider Factories

Factory providers execute a function to create the provider instance. Use when the provider needs runtime decisions or external input.

```typescript
{
  provide: 'PAYMENT_CLIENT',
  useFactory: (config: ConfigService, logger: LoggerService) => {
    const apiKey = config.get<string>('STRIPE_KEY');
    if (!apiKey) throw new Error('STRIPE_KEY not configured');
    return new StripeClient(apiKey, { logger });
  },
  inject: [ConfigService, LoggerService],
}
```

The `inject` array order must match the factory function parameter order exactly. Swapping the order gives you a ConfigService where you expected a LoggerService. TypeScript cannot catch this because `inject` is typed as `any[]`.

**Async Factory Providers:** NestJS awaits async factories during bootstrap. If the factory rejects, the application fails to start -- correct behavior. Never catch and swallow errors in factory providers; a failed dependency should prevent startup.

---

## Dynamic Module Patterns

**`forRoot(options)`**: Synchronous configuration. Use when all values are known at compile time. Mark `global: true` for app-wide singletons (database, cache).

**`forRootAsync(asyncOptions)`**: When config depends on other providers (ConfigService, secrets manager).

```typescript
static forRootAsync(options: CacheAsyncOptions): DynamicModule {
  return {
    module: CacheModule,
    global: true,
    imports: options.imports || [],  // CRITICAL -- must pass through
    providers: [
      { provide: 'CACHE_OPTIONS', useFactory: options.useFactory, inject: options.inject || [] },
      CacheService,
    ],
    exports: [CacheService],
  };
}
```

**Critical mistake:** Forgetting `imports: options.imports || []`. Without this, injected providers (like ConfigService) are unavailable in the dynamic module's DI context, causing "can't resolve dependencies" errors even though ConfigModule is imported at the app level.

**`forFeature(entities)`**: Per-module registration. Used by TypeORM/Mongoose to register entities/schemas within a feature module's scope.

---

## Injection Scope Performance

Benchmarked on a 4-core machine, NestJS v10, 1000 concurrent requests:

| Scope | Instances per 1000 Requests | Overhead per Request | Memory |
|-------|----------------------------|----------------------|--------|
| DEFAULT | 1 (singleton) | ~0 us | Baseline |
| REQUEST | 1000 x (provider + dependents) | 15-40 us | Linear growth |
| TRANSIENT | N x injections per request | 5-15 us per injection | Unpredictable |

**Scope Bubbling -- The Silent Performance Killer:**
If Provider A (DEFAULT) depends on Provider B (REQUEST), Provider A is automatically elevated to REQUEST scope. A single REQUEST-scoped logger cascades to 20+ providers becoming request-scoped.

**Detection:** Add `console.log(this.constructor.name, Date.now())` to constructors. If a "singleton" logs multiple times during load testing, scope bubbling has occurred.

**Workaround -- ModuleRef for Scope Isolation:**
When a singleton needs request-scoped data, inject `ModuleRef` and resolve manually:

```typescript
@Injectable()
export class NotificationService {
  constructor(private moduleRef: ModuleRef) {}
  async notify(contextId: ContextIdFactory) {
    const tenantSvc = await this.moduleRef.resolve(TenantService, contextId);
    // tenantSvc is request-scoped, NotificationService stays singleton
  }
}
```

---

## Multi-Provider Pattern

Register multiple implementations under the same token for plugin systems or strategy patterns:

```typescript
{ provide: 'VALIDATORS', useClass: EmailValidator, multi: true },
{ provide: 'VALIDATORS', useClass: PhoneValidator, multi: true },

@Injectable()
export class ValidationPipeline {
  constructor(@Inject('VALIDATORS') private validators: Validator[]) {}
  async validate(data: any) {
    return Promise.all(this.validators.map(v => v.validate(data)));
  }
}
```

---

## Provider Registration Order

Two providers with the same token: the LAST one wins (silent override). Factory providers with string/symbol tokens resolve strictly in registration order -- list dependencies before dependents.

---

## Interface-Based Injection

TypeScript interfaces are erased at runtime. You cannot use an interface as a DI token. Use abstract classes instead:

```typescript
// WRONG -- interface erased at runtime, DI fails silently
constructor(private readonly repo: IUserRepository) {}

// CORRECT -- abstract class preserved at runtime
export abstract class UserRepository {
  abstract findById(id: string): Promise<User>;
  abstract save(user: User): Promise<User>;
}
{ provide: UserRepository, useClass: PostgresUserRepository }
```

The abstract class serves as both a type contract and a DI token. It is never instantiated directly.
