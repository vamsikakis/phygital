# Gopalan Atlantis Facility Manager Frontend

This is the frontend for the Gopalan Atlantis Facility Manager application, built as a Progressive Web App (PWA) using React, Vite, and Material UI.

## Features

- **Progressive Web App**: Can be installed on mobile devices without an app store
- **Responsive Design**: Works on all screen sizes with mobile-first approach
- **Three Key Modules**:
  - **AKC (Apartment Knowledge Base)**: Access community documents and information
  - **OCE (Owners Communication & Engagement)**: View announcements, events, and polls
  - **HDC (Help Desk)**: Chat with AI assistant and manage service tickets

## Installation

1. Install dependencies:
   ```
   npm install
   ```

2. Create a `.env` file with the following content (adjust as needed):
   ```
   VITE_API_URL=http://localhost:5000/api
   ```

## Development

To start the development server:

```
npm run dev
```

The app will be available at http://localhost:5173

## Building for Production

To create a production build:

```
npm run build
```

The build output will be in the `dist` directory.

## Customization

### Theming

The app theme can be customized in `src/App.tsx` by modifying the theme object:

```tsx
const theme = createTheme({
  palette: {
    primary: {
      main: '#3f51b5', // Change to your primary color
    },
    secondary: {
      main: '#f50057', // Change to your secondary color
    },
    // Add more theme customizations here
  },
});
```

### Adding More Pages

1. Create a new page component in the `src/pages` directory
2. Add the route in `src/App.tsx`
3. Add navigation item in `src/components/Layout.tsx`

### PWA Configuration

PWA settings can be modified in `vite.config.ts` under the VitePWA plugin configuration. You can customize:

- App name and description
- Theme colors
- Icons
- PWA behaviors

## Browser Support

The app supports all modern browsers including:
- Chrome (desktop and mobile)
- Safari (desktop and mobile)
- Firefox
- Edge

For the best mobile experience, use Chrome on Android or Safari on iOS.
