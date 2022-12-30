import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  // Update state so the next render will show the fallback UI
  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  render() {
    return this.state.hasError ? <div className="alert alert-danger">Error rendering</div>
      : this.props.children;
  }
}

export async function fetcher(url) {
  const res = await fetch(url);
  if (res.status == 200) return await res.json();
  throw Error(`${res.status} ${await res.text()}`);
}
