// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import { themes as prismThemes } from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'OpenAssistants',
  tagline: 'OpenAssistants',
  favicon: 'img/definitive.ico',

  url: 'https://definitive-io.github.io',
  baseUrl: '/openassistants/',

  // GitHub pages deployment config.
  organizationName: 'definitive-io',
  projectName: 'openassistants',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl: 'https://github.com/definitive-io/openassistants',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl: 'https://github.com/definitive-io/openassistants',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'OpenAssistants',
        logo: {
          alt: 'Definitive logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Docs',
          },
          { to: '/blog', label: 'Blog', position: 'left' },
          {
            href: 'https://github.com/definitive-io/openassistants',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Getting started',
                to: '/docs/getting-started',
              },
              {
                label: 'Extending OpenAssistants',
                to: '/docs/category/extending-openassistants',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Discord',
                href: 'https://discord.gg/Snd4Cry7wD',
              },
              {
                label: 'X',
                href: 'https://x.com/DefinitiveIO',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/definitive-io/openassistants',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Definitive website',
                to: 'https://www.definitive.io/',
              },
              {
                label: 'LangChain',
                href: 'https://github.com/langchain-ai/langchain',
              },
            ],
          },
        ],
        copyright: `© ${new Date().getFullYear()} Definitive Intelligence Inc.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
