<script>
	import { Button, Range, Dropdown, DropdownItem } from 'flowbite-svelte';
	import {
		ChevronDownSolid,
		PlayOutline,
		AngleRightOutline,
		CloseOutline,
		CirclePauseOutline
	} from 'flowbite-svelte-icons';
	import { Playlist } from '../../components/playlist';
	import { onMount } from 'svelte';
	let websocket;
	let isPlaying = false;
	let isBreak = false;
	let volume = 50;
	let WsUrl = 'ws://127.0.0.1:8080/ws';
	let ready = false;
	let playlists;
	let url = 'http://127.0.0.1:8080';
	let currentPlaylist;
	let startActive = false;
	let playActive = false;
	$: {
		if (ready && websocket.readyState === WebSocket.OPEN) {
			handleVolumeChange(volume);
		}
	}

	function handlePlayPauseClick() {
		if (isPlaying) {
			websocket.send(JSON.stringify({ event: 'pause' }));
		} else {
			websocket.send(JSON.stringify({ event: 'resume' }));
		}
		playActive = !playActive;
	}

	function handleStartClick() {
		websocket.send(JSON.stringify({ event: 'next' }));
		startActive = !startActive;
	}

	function handleBreakClick() {
		if (!isBreak) {
			websocket.send(JSON.stringify({ event: 'break' }));
		} else {
			websocket.send(JSON.stringify({ event: 'nobreak' }));
		}

		isBreak = !isBreak;
	}

	async function handleDropdownItemClick(key) {
		let ps = await getPlayList(key);
		websocket.send(JSON.stringify({ event: 'load', playlist: key, position: 0 }));
	}

	// Function to handle WebSocket messages
	function handleWebSocketMessage(event) {
		const message = event.data;
		console.log('Received message:', message);
	}

	function handleVolumeChange(val) {
		console.log('volume', val);
		websocket.send(JSON.stringify({ event: 'volume', volume: val }));
	}

	onMount(() => {
		getPlaylistNames();
		websocket = new WebSocket(WsUrl);

		websocket.addEventListener('message', handleWebSocketMessage);
		ready = true;

		// Cleanup WebSocket connection on component unmount
		return () => {
			websocket.close();
		};
	});
	function getPlaylistNames() {
		return fetch(`${url}/playlist_names`)
			.then((response) => {
				if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
				}
				return response.json(); // Return the Promise from response.json()
			})
			.then((data) => {
				playlists = data.playlist_names;
				return data.playlist_names; // Return the extracted data
			})
			.catch((error) => {
				console.error('Error fetching playlist data:', error);
				throw error; // Propagate the error for further handling if needed
			});
	}

	async function getPlayList(playlist_name) {
		const playlistName = encodeURIComponent(playlist_name);
		let names = [];
		try {
			const response = await fetch(`${url}/playlist/${playlistName}`);
			const data = await response.json();
			let tracks = data[playlist_name];
			console.log(`playlist_name: ${playlist_name}`);
			currentPlaylist = new Playlist(playlist_name);
			console.log('         ');
			console.log(currentPlaylist);
			for (let i = 0; i < tracks.length; i++) {
				currentPlaylist.addTrack(tracks[i]);
			}
		} catch (error) {
			console.error('Error fetching playlist data:', error);
		}
		return currentPlaylist;
	}
</script>

<div class="w-2/6 p-2 bg-slate-700 m-auto mt-24">
	<div class="w-full">
		<Button
			class="bg-slate-800 hover:bg-slate-700 hover:outline hover:outline-slate-700 w-full mt-5 mb-8"
		>
			Playlists...
			<ChevronDownSolid class="w-4 h-4 ms-2 text-white dark:text-white" />
		</Button>
		<Dropdown>
			{#each playlists as key}
				<DropdownItem on:click={() => handleDropdownItemClick(key)}>{key}</DropdownItem>
			{/each}
		</Dropdown>
	</div>

	<div class="flex flex-row px-16 justify-around">
		<button class="btn" on:click={handleStartClick} class:active={startActive}>
			<AngleRightOutline class="m-auto text-slate-400 hover:text-slate-200" />
		</button>
		<button class="btn" on:click={handlePlayPauseClick} class:active={playActive}>
			{#if !isPlaying}
				<PlayOutline class="m-auto text-slate-400 hover:text-slate-200" />
			{:else}
				<CirclePauseOutline class="m-auto text-slate-400 hover:text-slate-200" />
			{/if}
		</button>

		<button class="btn" on:click={handleBreakClick}>
			<CloseOutline class="m-auto text-slate-400 hover:text-slate-200" />
		</button>
	</div>
	<div class="mt-5">
		<input type="range" class="slider progress" bind:value={volume} />
	</div>
</div>

<style>
	.slider {
		margin: 2em auto;
		width: 100%;
		height: 0.4em;
		-webkit-appearance: none;
		appearance: none;
		outline: none;
		border-radius: 3px;
		background: #1f1f1f;
		box-shadow:
			inset 3px 3px 6px #000,
			1px 1px 1px #909090;
	}

	.slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 1em;
		height: 1em;
		border-radius: 50%;
		background: #023e96;

		cursor: pointer;
		box-shadow: 0 0 0.5em #000;
	}

	.slider::-webkit-slider-thumb::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: #000;
		border-radius: 50%;
		box-shadow: 0 0 0.5em #000;
	}

	/* slider thumber hover */
	.slider::-webkit-slider-thumb:hover {
		background: #00317a;
		box-shadow: 0 0 0.5em #000;
	}

	.progress {
		width: 100%;
		height: 0.4em;
		background: linear-gradient(90deg, #4d83ff, #81a6ff);
		position: relative;
		top: -0.4em;
	}

	.btn {
		background: linear-gradient(-60deg, #4a4e5d, #272d39);
		border: none;
		box-shadow:
			0.3em 0.3em 0.8em #272d39,
			-0.3em -0.3em 0.6em #4a4e5d;
		width: 4em;
		height: 4em;
		align-content: center;
		justify-content: center;
		text-align: center;
		align-items: center;
		border-radius: 50%;
	}

	.btn:hover {
		color: #4d83ff;
		background: linear-gradient(-60deg, #4a4e5d, #161a23);
	}

	.active {
		color: #4d83ff;
		background: linear-gradient(-60deg, #34406e, #303c58);
	}
</style>
