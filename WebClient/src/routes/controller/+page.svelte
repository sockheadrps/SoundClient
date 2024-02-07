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
	let name;
	let current_song = undefined;
	let connected = false;
	let rx;
	let rx_timeout = undefined;
	let timeout = undefined;
	let paused = false;

	function handlePauseClick() {
			console.log('pause');
			websocket.send(JSON.stringify({ event: 'pause' }));
		playActive = !playActive;
	}
	function handlePlayClick() {
		websocket.send(JSON.stringify({ event: 'resume' }));
		console.log('resume');
		playActive = !playActive;
	}

	function handleStartClick() {
		console.log('start click');
		websocket.send(JSON.stringify({ event: 'next' }));
		if (!paused) {
			playActive = !playActive;
			
		}
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
		await getPlayList(key);
		name = key;
		websocket.send(JSON.stringify({ event: 'load', playlist: key, position: 0 }));
	}

	// Function to handle WebSocket messages
	function handleWebSocketMessage(event) {
		const message = JSON.parse(event.data);
		console.log(message);

		if (rx_timeout) {
			clearTimeout(rx);
		}

		rx = true;
		rx_timeout = setTimeout(() => {
			rx = false;
		}, 100);
		switch (message.event) {
			case 'playing':
				current_song = {
					title: message.song.title,
					artist: message.song.artist
				};
				break;
			case 'paused':
				paused = true;
				break;
			case 'next':
				break;
			case 'break':
				break;
			case 'load-paused':
				current_song = {
					title: message.song.title,
					artist: message.song.artist
				};
			case 'nobreak':
				break;
		}

		// console.log('Received message:', message);
	}
	function connectWebSocket() {
		try {
			websocket = new WebSocket(WsUrl);
			websocket.addEventListener('open', () => {
				console.log('WebSocket connection established.');
				getPlaylistNames();
				connected = true;
				clearTimeout(timeout);
			});
			websocket.addEventListener('message', handleWebSocketMessage);
			websocket.addEventListener('close', () => {
				console.log('WebSocket closed. Reconnecting...');
				name = undefined;
				current_song = false;
				connected = false;
				playActive = false;
				startActive = false;
				timeout = setTimeout(connectWebSocket, 3000);
			});
		} catch (error) {
			console.error('Error connecting to WebSocket:', error);
		}
	}

	onMount(() => {
		connectWebSocket();
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
				return response.json();
			})
			.then((data) => {
				playlists = data.playlist_names;
				return data.playlist_names;
			})
			.catch((error) => {
				console.error('Error fetching playlist data:', error);
				throw error;
			});
	}

	async function getPlayList(playlist_name) {
		const playlistName = encodeURIComponent(playlist_name);
		try {
			const response = await fetch(`${url}/playlist/${playlistName}`);
			const data = await response.json();
			let tracks = data[playlist_name];
			currentPlaylist = new Playlist(playlist_name);
			for (let i = 0; i < tracks.length; i++) {
				currentPlaylist.addTrack(tracks[i]);
			}
		} catch (error) {
			console.error('Error fetching playlist data:', error);
		}
		return currentPlaylist;
	}
</script>

<div class="w-2/6 p-2 bg-slate-700 m-auto mt-24 rounded-md">
	<div class="w-full">
		<button
			class=" bg-slate-800 m-auto w-5/6 h-10 mt-5 mb-4 flex justify-center items-center rounded-md dark:text-white dropdown"
		>
			{#if !name}
				<ChevronDownSolid class="w-4 h-4 ms-2 text-slate-400 dark:text-white" />
			{:else}
				<span class="text-slate-400">{name}</span>
			{/if}
		</button>
		<Dropdown>
			{#each playlists as key}
				<DropdownItem on:click={() => handleDropdownItemClick(key)}>{key}</DropdownItem>
			{/each}
		</Dropdown>
	</div>

	<div class="song-info mb-6 justify-center text-slate-400 flex flex-col">
		{#if current_song}
			<span class="flex justify-center">{current_song.title}</span>
			<span class="flex justify-center">{current_song.artist}</span>
		{/if}
	</div>

	<!-- start button -->
	<div class="flex flex-row px-16 justify-around">
		<button class="btn" on:click={handleStartClick} class:active={startActive}>
			<AngleRightOutline class="m-auto text-slate-400 hover:text-slate-200" />
		</button>

		<!-- pause / play -->
		{#if playActive}
			<button class="btn" on:click={handlePauseClick} class:active={!playActive}>
				<CirclePauseOutline class="m-auto text-slate-400 hover:text-slate-200" />
			</button>
		{:else if paused}
			<button class="btn" on:click={handlePlayClick} class:active={!playActive}>
				<PlayOutline class="m-auto text-slate-400 hover:text-slate-200" />
			</button>
		{:else}
			<button class="btn hidden"></button>
		{/if}

		<!-- close server -->
		<button class="btn" on:click={handleBreakClick}>
			<CloseOutline class="m-auto text-slate-400 hover:text-slate-200" />
		</button>
	</div>
	<div class="mt-5 flex">
		<input type="range" class="slider progress" bind:value={volume} />
	</div>
	<div>
		<div class="flex flex-row-reverse w-[80%] m-auto">
			<div class="flex flex-col">
				<div class="flex flex-row justify-end mb-2">
					<span class="text-gray-500 mx-2">Connected</span>
					<div class={connected ? 'led-connected' : 'led-disconnected'}></div>
				</div>
				<div class="flex flex-row justify-end">
					<span class="text-gray-500 mx-2">rx</span>
					<div>
						<div class="w-4 h-4 my-auto rounded-full {rx ? 'rx-rcv' : 'rx'}"></div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.slider {
		margin: 2em auto;
		width: 80%;
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
		background: #2b456c;
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
		background: #143463;
		box-shadow: 0 0 0.5em #000;
	}

	.progress {
		height: 0.4em;
		background: linear-gradient(90deg, #4d83ff, #81a6ff);
		position: relative;
		top: -0.4em;
	}

	.song-info {
		margin: 2em auto;
		width: 80%;
		height: 4em;
		-webkit-appearance: none;
		appearance: none;
		outline: none;
		border-radius: 3px;
		background: #1f1f1f;
		box-shadow:
			inset 3px 3px 6px #000,
			1px 1px 1px #504a4a;
	}

	.led-connected {
		background: linear-gradient(-60deg, #2f3e33, #359e53);
		border: none;
		box-shadow:
			0.3em 0.3em 0.8em #272d39,
			-0.3em -0.3em 0.6em #4a4e5d;
		width: 1rem;
		height: 1rem;
		align-content: center;
		justify-content: center;
		text-align: center;
		align-items: center;
		border-radius: 50%;
	}

	.led-disconnected {
		background: linear-gradient(-60deg, #6c3939, #ce2929);
		border: none;
		box-shadow:
			0.3em 0.3em 0.8em #272d39,
			-0.3em -0.3em 0.6em #4a4e5d;
		width: 1rem;
		height: 1rem;
		align-content: center;
		justify-content: center;
		text-align: center;
		align-items: center;
		border-radius: 50%;
	}

	.rx {
		background: linear-gradient(-60deg, #2f3e33, #608bc8);
		border: none;
		box-shadow:
			0.3em 0.3em 0.8em #272d39,
			-0.3em -0.3em 0.6em #4a4e5d;
		width: 1rem;
		height: 1rem;
		align-content: center;
		justify-content: center;
		text-align: center;
		align-items: center;
		border-radius: 50%;
	}

	.rx-rcv {
		background: linear-gradient(-60deg, #2f3e33, #60bcf9);
		border: none;
		box-shadow:
			0.3em 0.3em 0.8em #272d39,
			-0.3em -0.3em 0.6em #4a4e5d;
		width: 1rem;
		height: 1rem;
		align-content: center;
		justify-content: center;
		text-align: center;
		align-items: center;
		border-radius: 50%;
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

	.dropdown {
		background: linear-gradient(-10deg, #4a4e5d, #313949);
		border: none;
		box-shadow:
			0.3em 0.3em 0.8em #272d39,
			-0.3em -0.3em 0.6em #4a4e5d;
	}

	.dropdown:hover {
		background: linear-gradient(-10deg, #4a4e5d, #2d3447);
	}

	.btn:hover {
		color: #4d83ff;
		background: linear-gradient(-100deg, #4a4e5d, #202533);
	}

	.active {
		color: #4d83ff;
		background: linear-gradient(-60deg, #34406e, #303c58);
	}
</style>
