import { register } from 'register-service-worker'

export default function registerServiceWorker() {
  if (process.env.NODE_ENV === 'production') {
    register(`${process.env.PUBLIC_URL}/service-worker.js`, {
      ready() {
        console.log('Service Worker ready')
      },
      registered() {
        console.log('Service Worker registered')
      },
      cached() {
        console.log('Content has been cached for offline use')
      },
      updatefound() {
        console.log('New content is downloading')
      },
      updated() {
        console.log('New content is available; please refresh.')
      },
      offline() {
        console.log('No internet connection found. App is running in offline mode.')
      },
      error(error) {
        console.error('Error during service worker registration:', error)
      }
    })
  }
}
