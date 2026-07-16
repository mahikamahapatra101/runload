import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react' 

export default defineConfig({
  // Tells Vite to use the official React plugin to compile and hot-reload our components.
  plugins: [react()],
  
  server: {
    // Allows our custom domain (runload.local) to bypass Vite's host header safety check.
    // This is what prevents the "Blocked request" screen when we run on our custom local URL!
    allowedHosts: ['runload.local']
  }
})