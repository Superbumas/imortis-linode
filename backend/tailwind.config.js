module.exports = {
    content: [
      './templates/*.html',
      './static/js/*.js',
      // Add other paths to your template files here
    ],
    theme: {
      extend: {},
    },
    plugins: [
      require('@tailwindcss/forms'),
    ],
  }