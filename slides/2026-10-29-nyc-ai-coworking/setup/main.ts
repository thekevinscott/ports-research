// Presenter windows broadcast the mouse to every audience view; off for this deck.
export default () => {
  localStorage.setItem('slidev-presenter-cursor', 'false')
}
