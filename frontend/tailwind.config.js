module.exports = {
  theme: {
    extend: {
      animation: {
        'emoji-pop': 'emoji-pop 0.4s ease-out',
      },
      keyframes: {
        'emoji-pop': {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.4)' },
          '100%': { transform: 'scale(1)' },
        },
      },
    },
  },
};