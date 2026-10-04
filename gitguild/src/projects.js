/* All site content: collective copy plus the twelve project entries. */
window.GUILD = {
  collective: {
    name: 'Git Guild',
    subtitle: 'Developer Collective',
    lede: 'A student-first open-source collective. Every node in the mark below is a live repository — click one to open it.',
    since: 2024,
    links: {
      github: 'https://github.com/Git-Guild',
      chat: 'https://discord.com/',
      mail: 'mailto:hello@gitguild.dev'
    },
    quickstart: 'git clone https://github.com/Git-Guild/GitDeep.git'
  },

  projects: {
    n0: {
      name: 'GitDeep',
      tagline: 'GitHub account assessment via local AI models',
      blurb: 'Local AI assessment tool with Employer mode for hiring developers and Developer Mode providing tailored tips to level up your profile.',
      year: 2025, status: 'stable', featured: true,
      stack: ['TypeScript', 'Gemini', 'Ollama', 'Claude'],
      url: 'https://github.com/Git-Guild/GitDeep', repo: 'https://github.com/Git-Guild/GitDeep', docs: null
    },
    n1: {
      name: 'Git-Issue',
      tagline: 'Discover open-source issues to contribute',
      blurb: 'Unified portal that helps developers find issues to contribute from one website with streamlined, custom search.',
      year: 2025, status: 'stable', featured: true,
      stack: ['TypeScript', 'GitHub Actions', 'CI/CD'],
      url: 'https://github.com/Git-Guild/Git-Issue', repo: 'https://github.com/Git-Guild/Git-Issue', docs: null
    },
    n2: {
      name: 'Website',
      tagline: 'Interactive website & design tooling',
      blurb: 'The main website for the Git Guild developer collective, built with custom vector geometry and functional test automation.',
      year: 2025, status: 'stable',
      stack: ['JavaScript', 'HTML/CSS', 'Python', 'Playwright'],
      url: 'https://github.com/Git-Guild/Website', repo: 'https://github.com/Git-Guild/Website', docs: 'https://github.com/Git-Guild/Website/tree/main/docs'
    },
    n3: {
      name: 'CPP-Starting-from-0',
      tagline: 'Hands-on C++ fundamentals & OOP guide',
      blurb: 'Practical hands-on repository covering C++ object-oriented programming fundamentals, data structures, and beginner projects.',
      year: 2025, status: 'stable',
      stack: ['C++', 'OOP', 'Algorithms'],
      url: 'https://github.com/Git-Guild/CPP-Starting-from-0', repo: 'https://github.com/Git-Guild/CPP-Starting-from-0', docs: null
    },
    n4: {
      name: 'Python-Starting-from-0',
      tagline: 'Progressive beginner Python curriculum',
      blurb: 'A structured, beginner-friendly curriculum covering core Python concepts, scripts, and fundamental projects from absolute scratch.',
      year: 2025, status: 'stable',
      stack: ['Python', 'Python3', 'FreeCodeCamp'],
      url: 'https://github.com/Git-Guild/Python-Starting-from-0', repo: 'https://github.com/Git-Guild/Python-Starting-from-0', docs: null
    },
    n5: {
      name: 'JAVA-Starting-from-0',
      tagline: 'Comprehensive Java starter repository',
      blurb: 'A step-by-step learning guide for Java programming, OOP principles, and hands-on exercises designed for absolute beginners.',
      year: 2025, status: 'stable',
      stack: ['Java', 'OOP', 'Starter'],
      url: 'https://github.com/Git-Guild/JAVA-Starting-from-0', repo: 'https://github.com/Git-Guild/JAVA-Starting-from-0', docs: null
    },
    n6: {
      name: '.github',
      tagline: 'Community health & collective guidelines',
      blurb: 'Central health guidelines, contribution standards, and onboarding docs for the Git Guild student-first open-source collective.',
      year: 2024, status: 'stable',
      stack: ['Markdown', 'GitHub Actions', 'Community'],
      url: 'https://github.com/Git-Guild/.github', repo: 'https://github.com/Git-Guild/.github', docs: null
    },
    n7: {
      name: 'Warden',
      tagline: 'Policy-as-code for CI and secrets',
      blurb: 'Write access rules once in a small declarative language. Warden enforces them in CI, at deploy time and in your cloud account.',
      year: 2025, status: 'beta',
      stack: ['Go', 'OPA', 'Terraform'],
      url: 'https://github.com/Git-Guild/Website', repo: 'https://github.com/Git-Guild/Website', docs: null
    },
    n8: {
      name: 'Beacon',
      tagline: 'Observability for edge deploys',
      blurb: 'Streaming traces and structured logs from edge locations, sampled intelligently so you keep the requests that matter.',
      year: 2025, status: 'beta',
      stack: ['Rust', 'OpenTelemetry', 'ClickHouse'],
      url: 'https://github.com/Git-Guild/Website', repo: 'https://github.com/Git-Guild/Website', docs: null
    },
    n9: {
      name: 'Loom',
      tagline: 'Visual editor for pipeline DAGs',
      blurb: 'Drag a pipeline together, then export the exact YAML your CI already understands. Every graph is diffable and versioned.',
      year: 2025, status: 'beta',
      stack: ['React', 'YAML', 'D3'],
      url: 'https://github.com/Git-Guild/Website', repo: 'https://github.com/Git-Guild/Website', docs: null
    },
    n10: {
      name: 'Vector',
      tagline: 'Typed clients from OpenAPI spec',
      blurb: 'Point Vector at a spec and get a fully typed client, runtime validation and mock server. Regenerate on every upstream change.',
      year: 2025, status: 'experimental',
      stack: ['TypeScript', 'OpenAPI', 'Zod'],
      url: 'https://github.com/Git-Guild/Website', repo: 'https://github.com/Git-Guild/Website', docs: null
    },
    n11: {
      name: 'Bedrock',
      tagline: 'Infrastructure primitives & modules',
      blurb: 'The well-tested modules the rest of the collective is built on — networking, identity, queues and deploy plumbing.',
      year: 2024, status: 'stable',
      stack: ['Terraform', 'HCL', 'AWS'],
      url: 'https://github.com/Git-Guild/Website', repo: 'https://github.com/Git-Guild/Website', docs: null
    }
  },

  nodeClickBehavior: 'panel',

  mergeTrain: ['n11', 'n9', 'n6', 'n1', 'n5', 'n0'],

  order: ['n0', 'n3', 'n8', 'n10', 'n11', 'n9', 'n6', 'n2', 'n1', 'n5', 'n7', 'n4']
};
