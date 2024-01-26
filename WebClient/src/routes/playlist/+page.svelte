<script>
	import { Button, Dropdown, DropdownItem } from 'flowbite-svelte';
	import { ChevronDownSolid } from 'flowbite-svelte-icons';
	import { onMount } from 'svelte';

	let url = 'http://127.0.0.1:8080';
	let playlistData;
	let ready = false;
	let keys;
	let currentPlaylist = undefined;
	$: currentPlaylist = currentPlaylist;
	$: if (currentPlaylist !== undefined) {
		console.log(currentPlaylist.tracks);
		currentPlaylist.tracks = currentPlaylist.tracks;
	}

	onMount(async () => {
		try {
			const response = await fetch(`${url}/playlist`);
			const data = await response.json();
			playlistData = data.Masterlist;
			getSongsFromPlaylist('My playlist');

			keys = Object.keys(playlistData);
		} catch (error) {
			console.error('Error fetching playlist data:', error);
		}
		ready = true;
	});

	function getSongsFromPlaylist(playlist_name) {
		let songs = [];
		for (let i = 0; i < playlistData[playlist_name].length; i++) {
			songs.push(playlistData[playlist_name][i]);
		}
		return songs;
	}

	function handleDropdownItemClick(key) {
		let tracks = getSongsFromPlaylist(key);
		currentPlaylist = new Playlist(key);
		for (let i = 0; i < tracks.length; i++) {
			currentPlaylist.addTrack(tracks[i]);
		}
	}

	function Playlist(name) {
		this.name = name;
		this.tracks = []; 
		this.cursorAt = 0;
		this.selection = undefined;
		this.insertMode = 'insert';

		this.addTrack = function (track) {
			this.tracks.push(track);
		};

		this.savePlaylist = function () {
			const data = {
				name: this.name,
				media: this.tracks
			};
			const saveEndpoint = `${url}/save_playlist`;
			const options = {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(data)
			};
			fetch(saveEndpoint, options)
				.then((response) => {
					if (!response.ok) {
						console.log('response, ', response);
						throw new Error('Network response was not ok');
					}
					return response.json();
				})
				.then((data) => {
					console.log('Playlist saved successfully:', data);
					// Handle the response data as needed
				})
				.catch((error) => {
					console.error('Error saving playlist:', error);
					// Handle errors if the request fails
				});
		};

		this.handleKeyEvent = function (event) {
			if (event.key === 'ArrowUp') {
				if (this.insertMode == 'delete') {
					currentPlaylist.insertMode = "insert"
					currentPlaylist.selection = undefined
				}
				if (this.cursorAt > 0) {
					this.cursorAt--;
				}
				currentPlaylist.cursorAt = this.cursorAt;
			}

			if (event.key === 'ArrowDown') {
				if (this.cursorAt < this.tracks.length - 1) {
					this.cursorAt++;
				}
				currentPlaylist.cursorAt = this.cursorAt;
			}

			if (event.key === 'i') {
				this.insertMode = 'insert';
				currentPlaylist.insertMode = this.insertMode;
			}

			if (event.key === 's') {
				this.insertMode = 'swap';
				currentPlaylist.insertMode = this.insertMode;
			}

			if (event.key === 'd') {
				this.insertMode = 'delete';
				currentPlaylist.insertMode = this.insertMode;
			}

			if (event.key === 'Enter') {
				if (this.selection === undefined) {
					this.selection = this.cursorAt;
					currentPlaylist.tracks = currentPlaylist.tracks;
					return;
				}
				if (this.selection !== undefined && this.insertMode == 'insert') {
					if (this.selection == this.cursorAt) {
						return;
					}
					let selected_item = this.tracks[this.selection];
					let moving_item = this.tracks[this.cursorAt];
					if (this.selection < this.cursorAt) {
						this.tracks.splice(this.selection, 1);
						this.tracks.splice(this.cursorAt - 1, 1, selected_item, moving_item);
					} else {
						this.tracks.splice(this.selection, 1);
						this.tracks.splice(this.cursorAt, 1, selected_item, moving_item);
					}

					let tracks = this.tracks;
					currentPlaylist.tracks = tracks;
					this.selection = undefined;
				} else if (this.selection !== undefined && this.insertMode == 'swap') {
					let tracks = currentPlaylist.tracks;

					[tracks[this.cursorAt], tracks[this.selection]] = [
						tracks[this.selection],
						tracks[this.cursorAt]
					];

					currentPlaylist.tracks = tracks;
					this.selection = undefined;
				} else if (this.selection !== undefined && this.insertMode == 'delete') {
					this.tracks.splice(this.selection, 1);
					let tracks = this.tracks;
					currentPlaylist.tracks = tracks;
					this.selection = undefined;
				}
				this.savePlaylist();
			}
		};

		// Add event listener for key events
		document.addEventListener('keydown', this.handleKeyEvent.bind(this));
	}
</script>

{#if ready}
	<div class="flex items-center justify-center mt-20">
		<!-- colored container -->
		<div class="card w-5/6 h-5/6 items-start flex flex-col">
			<div class="w-full flex -my-6 row-auto">
				<Button
				class="ml-12 bg-slate-800 hover:bg-slate-700 hover:outline hover:outline-slate-700"
			>
				{#if currentPlaylist === undefined}
					Playlists...
					<ChevronDownSolid class="w-4 h-4 ms-2 text-white dark:text-white" />
				{:else}
					{currentPlaylist.name}
				{/if}
			</Button>
				<Dropdown>
					{#each keys as key}
						<DropdownItem on:click={() => handleDropdownItemClick(key)}>{key}</DropdownItem>
					{/each}
					<DropdownItem>New Playlist...</DropdownItem>
				</Dropdown>
			</div>

			<div class="w-[90%] h-[90%] mt-20 rounded-md">
				{#if currentPlaylist}
					<div class="h-[95%] overflow-hidden overflow-x-auto overflow-y-auto scroll">
						<table class="min-w-full divide-y divide-none">
							<thead class="bg-transparent">
								<tr>
									<th
										scope="col"
										class="pb-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
									>
									</th>
									<th
										scope="col"
										class="pr-6 pb-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
										>Artist</th
									>
									<th
										scope="col"
										class="px-6 pb-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
										>Song</th
									>
									<th
										scope="col"
										class="px-6 pb-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
										>File Path</th
									>
								</tr>
							</thead>
							<tbody class="bg-transparent divide-none">
								{#each currentPlaylist.tracks as song, idx}
									<tr class="h-8 m-auto">
										{#if currentPlaylist.cursorAt == idx}
											<td class="py-1 text-cyan-500 text-xs text-nowrap align-top pr-2">&gt;</td>
										{:else}
											<td class=" py-1 text-cyan-500 text-xs text-nowrap align-top"></td>
										{/if}

										{#if currentPlaylist.selection == idx}
											{#if currentPlaylist.insertMode == 'delete'}
												<td class="pr-3 py-1 text-red-400 text-xs text-nowrap align-top"
													>{song.artist}</td
												>
												<td
													class="px-6 py-1 text-red-400 text-xs text-nowrap align-top text-left"
													>{song.title}</td
												>
												<td
													class="px-6 py-1 text-red-400 text-xs text-nowrap align-top text-left"
													>{song.file_path}</td
												>
											{:else}
												<td class="pr-3 py-1 text-primary-400 text-xs text-nowrap align-top"
													>{song.artist}</td
												>
												<td
													class="px-6 py-1 text-primary-400 text-xs text-nowrap align-top text-left"
													>{song.title}</td
												>
												<td
													class="px-6 py-1 text-primary-400 text-xs text-nowrap align-top text-left"
													>{song.file_path}</td
												>
											{/if}
										{:else}
											<td class="pr-3 py-1 text-cyan-500 text-xs text-nowrap align-top"
												>{song.artist}</td
											>
											<td class="px-6 py-1 text-cyan-500 text-xs text-nowrap align-top text-left"
												>{song.title}</td
											>
											<td class="px-6 py-1 text-cyan-500 text-xs text-nowrap align-top text-left"
												>{song.file_path}</td
											>
										{/if}
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{:else}
					<p>Loading...</p>
				{/if}
				{#if currentPlaylist !== undefined}
					<div class="w-full h-10 flex flex-row-reverse">
						<div class="flex flex-row">
							<h1 class="text-lg text-slate-600 pr-2">Mode:</h1>
							<h1 class="text-xl font-bold text-slate-400">{currentPlaylist.insertMode}</h1>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	@property --rotate {
		syntax: '<angle>';
		initial-value: 132deg;
		inherits: false;
	}

	:root {
		--card-height: 85vh;
		--card-width: calc(var(--card-height) * 1.2);
	}

	.card {
		background: #191c29;
		width: var(--card-width);
		height: var(--card-height);
		padding: 3px;
		position: relative;
		border-radius: 6px;
		align-items: center;
		text-align: center;
		display: flex;
		font-size: 1.5em;
		color: rgb(88 199 250 / 0%);
		font-family: cursive;
	}

	.card::before {
		content: '';
		width: 101%;
		height: 101%;
		border-radius: 10px;
		background-image: linear-gradient(var(--rotate), #5ddcff95, #3c66e36f 43%, #4e00c2);
		position: absolute;
		z-index: -1;
		top: -0.5%;
		left: -0.5%;
		animation: spin 10s linear infinite;
	}

	@keyframes spin {
		0% {
			--rotate: 0deg;
		}
		100% {
			--rotate: 360deg;
		}
	}

	.scroll::-webkit-scrollbar {
		background: rgba(0, 0, 0, 0);
		display: block;
	}
	.scroll::-webkit-scrollbar-track {
		border-radius: 10px;
		background-clip: padding-box;
	}
	.scroll::-webkit-scrollbar-track-piece:end {
		background: transparent;
	}
	.scroll::-webkit-scrollbar-track-piece:start {
		background: transparent;
	}
	.scroll::-webkit-scrollbar-thumb {
		background: rgb(44, 44, 44);
		border-radius: 10px;
		border: 5px solid #0000;
		background-clip: padding-box;
	}
	.scroll::-webkit-scrollbar-thumb:hover {
		background: #222;
		background-clip: padding-box;
	}
	.scroll::-webkit-scrollbar-corner {
		background: transparent;
	}
	::-webkit-scrollbar {
		height: 0; /* Set height to 0 */
		display: none; /* Hide the scrollbar */
	}

	.active {
		background-color: #ff3e00;
		color: white;
	}
</style>
