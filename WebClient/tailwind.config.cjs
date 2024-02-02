/** @type {import('tailwindcss').Config} */
export default {
	content: [
		'./src/**/*.{html,js,svelte,ts}',
		'./node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}'
	],
	plugins: [require('flowbite/plugin')],

	darkMode: 'class',
	theme: {
		extend: {
			fontFamily: {
				mono: ['monospace'],
			  },
			colors: {
				// flowbite-svelte
				primary: {
					50: '#F2F6FF',
					100: '#E6EEFF',
					200: '#C2D4FF',
					300: '#A2B8FF',
					400: '#6690FF',
					500: '#3366FF', // Adjusted to a blue hue
					600: '#254EDB',
					700: '#1F45C3',
					800: '#173A97',
					900: '#0F2F6D',
				}
			}
		}
	}
};
