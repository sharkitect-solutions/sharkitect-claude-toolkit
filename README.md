# Sharkitect Claude Toolkit

Personal Claude Code skill library and setup guide. Contains 111 custom skills and a complete install guide to restore or replicate this environment from any machine.

## Quick Start

1. Install Claude Code and authenticate
2. Follow [INSTALL-GUIDE.md](INSTALL-GUIDE.md) to set up plugins, MCP servers, and marketplaces
3. Copy skills: `cp -r skills/* ~/.claude/skills/`

## What's Included

### Custom Skills (111)

Skills live in the `skills/` directory. Each skill has a `SKILL.md` file and optional reference/example subdirectories.

#### Development & Architecture
| Skill | Description |
|-------|-------------|
| `clean-code` | Pragmatic coding standards |
| `deslop` | Remove AI-generated code slop |
| `docker-expert` | Docker containerization |
| `error-resolver` | Systematic error diagnosis |
| `find-bugs` | Bug and vulnerability detection |
| `frontend-design` | Production-ready frontend design |
| `nestjs-expert` | NestJS framework specialist |
| `nextjs-best-practices` | Next.js App Router principles |
| `security-best-practices` | Security scanning |
| `senior-architect` | Software architecture |
| `senior-backend` | Backend development |
| `systematic-debugging` | Structured debugging methodology |
| `vulnerability-scanner` | Advanced vulnerability analysis |

#### AI & Agents
| Skill | Description |
|-------|-------------|
| `agent-development` | Building agents |
| `agent-evaluation` | Testing/benchmarking agents |
| `agent-memory-systems` | Memory for intelligent agents |
| `agents-autogpt` | AutoGPT platform |
| `agents-crewai` | CrewAI multi-agent orchestration |
| `agents-llamaindex` | LlamaIndex data framework |
| `ai-agents-architect` | AI agent design |
| `prompt-engineering-guidance` | LLM prompt control |
| `voice-agents` | Voice agent development |
| `voice-ai-development` | Voice AI applications |

#### n8n Automation
| Skill | Description |
|-------|-------------|
| `n8n-code-javascript` | JavaScript in n8n Code nodes |
| `n8n-code-python` | Python in n8n Code nodes |
| `n8n-expression-syntax` | n8n expression validation |
| `n8n-mcp-tools-expert` | n8n MCP tools guide |
| `n8n-node-configuration` | n8n node setup |
| `n8n-validation-expert` | n8n validation errors |
| `n8n-workflow-patterns` | n8n workflow architecture |

#### Marketing & Sales
| Skill | Description |
|-------|-------------|
| `cold-email` | B2B cold email writing |
| `competitive-ads-extractor` | Competitor ad analysis |
| `competitor-alternatives` | Alternative comparison pages |
| `content-creator` | SEO content creation |
| `content-research-writer` | Research-based writing |
| `email-composer` | Professional email drafting |
| `email-draft-polish` | Email QA |
| `email-sequence` | Email sequence building |
| `email-systems` | Email marketing systems |
| `executing-marketing-campaigns` | Campaign execution |
| `launch-strategy` | Product launch planning |
| `lead-research-assistant` | Lead identification |
| `marketing-demand-acquisition` | Demand generation |
| `marketing-ideas` | Marketing ideation |
| `marketing-psychology` | Psychology-based marketing |
| `marketing-strategy-pmm` | Product marketing strategy |
| `outreach-specialist` | B2B outreach |
| `social-content` | Social media content |

#### CRO & Conversion
| Skill | Description |
|-------|-------------|
| `form-cro` | Form optimization |
| `onboarding-cro` | Onboarding optimization |
| `page-cro` | Landing page CRO |
| `paywall-upgrade-cro` | Paywall/upgrade flows |
| `popup-cro` | Popup creation |
| `signup-flow-cro` | Signup flow optimization |

#### Business & Strategy
| Skill | Description |
|-------|-------------|
| `ceo-advisor` | Executive leadership |
| `cto-advisor` | Technical leadership |
| `pricing-strategy` | Pricing optimization |
| `product-manager-toolkit` | Product management |
| `product-strategist` | Product strategy |
| `free-tool-strategy` | Free tool planning |
| `game-changing-features` | 10x product opportunities |
| `micro-saas-launcher` | Micro-SaaS launches |
| `referral-program` | Referral programs |

#### Document & Content Generation
| Skill | Description |
|-------|-------------|
| `docx` | Word document creation |
| `pptx` | PowerPoint creation |
| `xlsx` | Spreadsheet creation |
| `pdf-processing-pro` | PDF processing |
| `documentation-templates` | Doc templates |
| `writing-clearly-and-concisely` | Clear prose writing |

#### Skill & Plugin Development
| Skill | Description |
|-------|-------------|
| `ultimate-skill-creator` | Unified skill creation (hybrid of 3 tools) |
| `skill-creator` | Skill creation with eval pipeline |
| `skill-judge` | Skill quality evaluation |
| `hook-development` | Hook creation |
| `mcp-integration` | MCP server integration |

### Install Guide

See [INSTALL-GUIDE.md](INSTALL-GUIDE.md) for the complete setup:
- Plugin marketplace registration
- Tier 1/2/3 plugin installation commands
- MCP server configuration
- Skill installation
- Verification steps

## Updating

When you create or modify skills:

```bash
# Copy updated skill into repo
cp -r ~/.claude/skills/<skill-name> skills/<skill-name>

# Commit and push
git add .
git commit -m "Update <skill-name>"
git push
```

## Restoring on a New Machine

```bash
git clone https://github.com/YOUR_USERNAME/sharkitect-claude-toolkit.git
cp -r sharkitect-claude-toolkit/skills/* ~/.claude/skills/
# Then follow INSTALL-GUIDE.md for plugins and MCP servers
```
