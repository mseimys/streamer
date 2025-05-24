# React App with FastAPI Static Serving

This is a simple React app (Vite + React Router) with routes `/page1` and `/page2`, designed to be served as static files by FastAPI under the `/app/` prefix.

## Features

- React Router with `/page1` and `/page2` routes
- Handles `/app/` prefix for correct routing when served from FastAPI

## Development

```sh
npm install
npm run dev
```

## Production Build

```sh
npm run build
```

The static files will be output to the `dist/` directory.

## Serving with FastAPI

- Mount the `dist/` directory as static files in FastAPI under the `/app/` prefix.
- Ensure FastAPI is configured to serve all routes (including subroutes) to `index.html` for client-side routing.

## Nginx

- The provided nginx config proxies `/app/` to FastAPI.

---

This project was bootstrapped with [Vite](https://vitejs.dev/) and [React](https://react.dev/).
