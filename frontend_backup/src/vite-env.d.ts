/// <reference types="vite/client" />

declare module 'react' {
  export = React;
  namespace React {
    type ReactNode = any;
    type FC<P = {}> = (props: P) => any;
    interface CSSProperties {
      [key: string]: any;
    }
  }
  const React: any;
}

declare module 'react/jsx-runtime' {
  export const jsx: any;
  export const jsxs: any;
  export const Fragment: any;
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}
