<script>
	import { PUBLIC_API } from '$env/static/public';

	import { Button, Dropdown, DropdownItem } from 'flowbite-svelte';
	import { ChevronDownSolid } from 'flowbite-svelte-icons';
	import { onMount } from 'svelte';
	import SongList from '../../components/SongList.svelte';
	let url = `http://${PUBLIC_API}`;
	let ready = false;
	let keys;
	let currentPlaylist;
	let openSongList = false;
	let cursorAt = 0;

	class Playlist {
		constructor({ name }) {
			this.name = name;
			this.tracks = [];
			this.cursorAt = 0;
			this.selection = undefined;
			this.insertMode = 'insert';
			this.pause = false;
			this.currentTrack = undefined;

			this.addTrack = function (track) {
				this.tracks.push(track);
			};

			this.savePlaylist = function () {
				const data = {
					name: this.name,
					media: this.tracks
				};
				const saveEndpoint = `${url}/${this.name}/update`;
				const options = {
					method: 'PUT',
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
					})
					.catch((error) => {
						console.error('Error saving playlist:', error);
					});
			};

			this.handleKeyEvent = function (event) {
				if (!this.pause) {
					switch (event.key) {
						case 'ArrowUp':
							if (this.insertMode == 'delete') {
								this.insertMode = 'insert';
								this.selection = undefined;
							}
							if (this.cursorAt > 0) {
								this.cursorAt--;
							}
							break;

						case 'ArrowDown':
							if (this.insertMode == 'delete') {
								this.insertMode = 'insert';
								this.selection = undefined;
							}
							if (this.cursorAt < this.tracks.length - 1) {
								this.cursorAt++;
							}

							break;

						case 'a':
							this.pause = true;
							openSongList = !openSongList;
							break;

						case 'i':
							this.insertMode = 'insert';
							break;

						case 's':
							this.insertMode = 'swap';
							break;

						case 'd':
							this.insertMode = 'delete';
							break;

						case 'Enter':
							if (this.selection === undefined && this.insertMode !== 'delete') {
								this.selection = this.cursorAt;
							} else if (this.selection === undefined && this.insertMode === 'delete') {
								this.tracks.splice(this.cursorAt, 1);
								this.savePlaylist();
								this.selection = undefined;
							} else if (this.selection !== undefined && this.insertMode == 'insert') {
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

								this.savePlaylist();
								this.selection = undefined;
							} else if (this.selection !== undefined && this.insertMode == 'swap') {
								let tracks = currentPlaylist.tracks;
								[tracks[this.cursorAt], tracks[this.selection]] = [
									tracks[this.selection],
									tracks[this.cursorAt]
								];
								this.savePlaylist();
								this.selection = undefined;
							}
							break;
					}
					let tracks = this.tracks;
					currentPlaylist.tracks = tracks;
					cursorAt = this.cursorAt;
				}
			};
			document.addEventListener('keydown', this.handleKeyEvent.bind(this));
		}
	}

	function saveNewPlaylist(name, tracks) {
		const data = {
			name: name,
			media: tracks
		};
		console.log('data:', data);
		const saveEndpoint = `${url}/${name}/update`;
		const options = {
			method: 'PUT',
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
			})
			.catch((error) => {
				console.error('Error saving playlist:', error);
			});
	}

	async function deletePlaylist() {
		if (!currentPlaylist) {
			return;
		}
		keys = [];
		const data = {
			name: currentPlaylist.name
		};
		const saveEndpoint = `${url}/${currentPlaylist.name}/delete`;
		const options = {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
		};

		try {
			const response = await fetch(saveEndpoint, options);

			if (!response.ok) {
				console.error('Error:', response.status, response.statusText);
				throw new Error('Network response was not ok');
			}

			const deleteData = await response.json();
			console.log('Playlist deleted successfully:', deleteData);

			// Assuming keys is a global variable
			currentPlaylist = undefined;
			keys = await getPlaylistNames();
		} catch (error) {
			console.error('Error deleting playlist:', error);
		}
	}

	async function getPlaylistNames() {
		let names = [];
		try {
			const response = await fetch(`${url}/playlist_names`);
			const data = await response.json();
			for (let i = 0; i < data.playlist_names.length; i++) {
				names.push(data.playlist_names[i]);
			}
		} catch (error) {
			console.error('Error fetching playlist data:', error);
		}
		return names;
	}

	async function getPlayList(playlist_name) {
		const playlistName = encodeURIComponent(playlist_name);
		try {
			const response = await fetch(`${url}/playlist/${playlistName}`);
			const data = await response.json();
			console.log('Playlist data:', data);
			let tracks = data[playlist_name];
			currentPlaylist = new Playlist({ name: playlist_name, cursorAt: cursorAt });
			for (let i = 0; i < tracks.length; i++) {
				currentPlaylist.addTrack(tracks[i]);
			}
		} catch (error) {
			console.error('Error fetching playlist data:', error);
		}
	}

	onMount(async () => {
		keys = await getPlaylistNames();
		ready = true;
	});

	async function handleDropdownItemClick(key) {
		if (key === 'new') {
			let name = prompt('Enter new playlist name');
			currentPlaylist = new Playlist(name);
			saveNewPlaylist(name, currentPlaylist.tracks);
		} else {
			console.log('key:', key);
			await getPlayList(key);
		}
	}
</script>

{#if ready}
	{#if openSongList && currentPlaylist}
		<SongList bind:tracks={currentPlaylist.tracks} bind:openSongList {currentPlaylist} />
	{/if}
	{#if !openSongList}
		<div class="flex items-center justify-center mt-20">
			<!-- colored container -->
			<div class="card w-5/6 h-5/6 items-start flex flex-col">
				<div class="w-full flex mt-3 row-auto">
					{#if currentPlaylist}
						<!-- delete button -->
						<Button
							class="ml-12 mr-2 bg-transparent border-2 border-red-500"
							on:click={() => deletePlaylist()}>❌</Button
						>
					{:else}
						<!-- ghost button -->
						<Button class="ml-12 mr-2 bg-transparent disabled hover:bg-transparent cursor-default"
						></Button>
					{/if}

					<!-- Playlist dropdown -->
					<Button class="bg-slate-800 hover:bg-slate-700 hover:outline hover:outline-slate-700">
						{#if currentPlaylist === undefined}
							Playlists...
							<ChevronDownSolid class="w-4 h-4 ms-2 text-white dark:text-white" />
						{:else}
							{currentPlaylist.name}
						{/if}
					</Button>
					{#if keys}
						<Dropdown>
							{#each keys as key}
								<DropdownItem on:click={() => handleDropdownItemClick(key)}>{key}</DropdownItem>
							{/each}
							<DropdownItem on:click={() => handleDropdownItemClick('new')}
								>New Playlist...</DropdownItem
							>
						</Dropdown>
					{/if}
				</div>

				<div class="w-[90%] h-[90%] mt-20 rounded-md overflow-hidden">
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
									</tr>
								</thead>
								<tbody class="bg-transparent divide-none">
									{#each currentPlaylist.tracks as song, idx}
										<tr
											class="h-8 m-auto text-sm"
											class:active={cursorAt === idx}
											class:item={cursorAt !== idx}
											class:delete={cursorAt === idx && currentPlaylist.insertMode === 'delete'}
										>
											{#if cursorAt === idx}
												<td class="py-1 text-nowrap align-top pr-2">&gt;</td>
											{:else}
												<td class="py-1 text-nowrap align-top"></td>
											{/if}

											{#if idx === currentPlaylist.selection}
												<td class="selected pr-3 py-1 text-nowrap align-top text-left"
													>{song.artist}</td
												>
												<td class="selected py-1 text-nowrap align-top text-left">{song.title}</td>
											{:else}
												<td class="pr-3 py-1 text-left text-nowrap align-top">{song.artist}</td>
												<td class="py-1 text-nowrap align-top text-left">{song.title}</td>
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
		font-size: 16px;
		color: rgb(90, 181, 255);
	}
	.selected {
		font-size: 16px;
		color: rgb(73, 172, 239);
	}
	.delete {
		color: #ff0000;
	}

	.item {
		color: rgb(31, 112, 218);
	}
</style>
