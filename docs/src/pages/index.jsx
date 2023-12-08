import React from 'react';
import { Redirect } from '@docusaurus/router';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  const { baseUrl } = siteConfig;

  // Now you can use baseUrl in your component
  // For example, to redirect to a page:
  return <Redirect to={`${baseUrl}docs/getting-started`} />;
}
