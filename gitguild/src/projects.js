/* All site content: collective copy plus the twelve project entries. */
window.GUILD = {
  collective: {
    name: 'Git Guild',
    subtitle: 'Developer Collective',
    lede: 'Twelve projects, one network. Every node in the mark below is a live repository — click one to open it.',
    since: 2026,
    links: {
      github: 'https://github.com/Git-Guild',
      chat: 'https://discord.com/',
      mail: 'mailto:hello@gitguild.dev',
      docs: 'https://github.com/Git-Guild',
      goodFirstIssues: 'https://github.com/search?q=good-first-issue&type=issues'
    },
    quickstart: 'npx @gitguild/cli open <project>'
  },

  projects: {
    n0: {
      name: 'Anchor',
      tagline: 'Zero-config release automation',
      blurb: 'Cut a versioned release from any branch in a monorepo with one command. Anchor derives the bump from conventional commits, writes the changelog, tags the commit and runs your publish graph in dependency order.',
      year: 2026, status: 'stable', featured: true,
      stack: ['TypeScript', 'Node', 'GitHub Actions'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: null
    },
    n1: {
      name: 'Guild CLI',
      tagline: 'The hub that ties every tool together',
      blurb: 'One binary, twelve plugins. The CLI discovers the rest of the collective on install and exposes each project as a namespaced command, so the whole toolchain is one `guild` away.',
      year: 2026, status: 'stable',
      stack: ['Go', 'Cobra', 'gRPC'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: 'https://github.com/'
    },
    n2: {
      name: 'Lattice',
      tagline: 'Composable GraphQL federation',
      blurb: 'Describe a schema once, compose it anywhere. Lattice splits a graph into independently deployable services and stitches them back together at the edge with query-plan caching.',
      year: 2026, status: 'stable',
      stack: ['TypeScript', 'GraphQL', 'Redis'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: null
    },
    n3: {
      name: 'Beacon',
      tagline: 'Observability for edge deploys',
      blurb: 'Streaming traces and structured logs from hundreds of edge locations, sampled intelligently so you keep the requests that matter and drop the noise.',
      year: 2026, status: 'stable',
      stack: ['Rust', 'OpenTelemetry', 'ClickHouse'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: null
    },
    n4: {
      name: 'Prism',
      tagline: 'Deterministic UI snapshot tests',
      blurb: 'Renders every component state in a real browser and diffs it against a committed baseline. Fonts, clocks and randomness are frozen, so a failure always means a real visual change.',
      year: 2026, status: 'beta',
      stack: ['TypeScript', 'Playwright', 'Vite'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: null
    },
    n5: {
      name: 'Cinder',
      tagline: 'A bundler that respects the network',
      blurb: 'Content-addressed builds with per-route budgets. Cinder fails a pull request the moment a bundle crosses its weight budget, and tells you exactly which import did it.',
      year: 2026, status: 'stable',
      stack: ['Rust', 'SWC', 'WASM'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: null
    },
    n6: {
      name: 'Warden',
      tagline: 'Policy-as-code for CI and secrets',
      blurb: 'Write access rules once in a small declarative language. Warden enforces them in CI, at deploy time and in your cloud account, with a dry-run diff before anything changes.',
      year: 2026, status: 'stable',
      stack: ['Go', 'OPA', 'Terraform'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: 'https://github.com/'
    },
    n7: {
      name: 'Loom',
      tagline: 'Visual editor for pipeline DAGs',
      blurb: 'Drag a pipeline together, then export the exact YAML your CI already understands. Every graph is diffable, reviewable and versioned like ordinary source.',
      year: 2026, status: 'beta',
      stack: ['React', 'YAML', 'D3'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: null
    },
    n8: {
      name: 'Vector',
      tagline: 'Typed clients from any OpenAPI spec',
      blurb: 'Point Vector at a spec and get a fully typed client, runtime validation and mock server. Regenerate on every upstream change so client drift stops being a category of bug.',
      year: 2026, status: 'stable',
      stack: ['TypeScript', 'OpenAPI', 'Zod'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: null
    },
    n9: {
      name: 'Kiln',
      tagline: 'Reproducible dev environments in seconds',
      blurb: 'Declare the services, databases and fixtures a task needs. Kiln boots them from a warm content-addressed cache and tears the whole thing down when you are done.',
      year: 2026, status: 'stable',
      stack: ['Rust', 'containerd', 'Nix'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: null
    },
    n10: {
      name: 'Ferry',
      tagline: 'Schema migrations with real dry-runs',
      blurb: 'Moves data between shapes safely: expand, backfill, verify, contract. Ferry estimates row counts and lock impact before you approve, and can roll a half-finished migration back.',
      year: 2026, status: 'stable',
      stack: ['Python', 'Postgres', 'SQL'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: null
    },
    n11: {
      name: 'Bedrock',
      tagline: 'Infrastructure primitives, as modules',
      blurb: 'The boring, well-tested modules the rest of the collective is built on — networking, identity, queues and deploy plumbing. Composable, documented and versioned.',
      year: 2026, status: 'stable',
      stack: ['Terraform', 'HCL', 'AWS'],
      url: 'https://github.com/', repo: 'https://github.com/', docs: 'https://github.com/'
    }
  },

  nodeClickBehavior: 'page',

  mergeTrain: ['n11', 'n9', 'n6', 'n1', 'n5', 'n0'],

  order: ['n0', 'n3', 'n8', 'n10', 'n11', 'n9', 'n6', 'n2', 'n1', 'n5', 'n7', 'n4']
};
