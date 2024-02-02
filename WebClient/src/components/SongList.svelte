<script>
	import { onMount, onDestroy } from 'svelte';
	let ready = false;
	let mediaList = undefined;
	export let tracks = undefined;
	export let currentPlaylist;
	let presentTracks = undefined;
	let presentIndicies = [];
	let persistCursor = undefined;
	export let openSongList;
	class Media {
		constructor() {
			this.url = 'http://127.0.0.1:8080/media';
			this.mediaData = null; // Variable to store media data
			this.cursorAt = 0;
			this.fetchMediaData();
			if (mediaList) {
				this.mediaData = mediaList;
				this.cursorAt = persistCursor;
			}
		}

		async fetchMediaData() {
			try {
				const response = await fetch(`${this.url}`);
				if (!response.ok) {
					throw new Error(`Failed to fetch media data. Status: ${response.status}`);
				}

				this.mediaData = await response.json();
				let media = this.mediaData.media['All Media'];
				console.log('Media data fetched successfully:', this.mediaData);
				this.mediaData = media;
				mediaList = media;
				presentTracks = tracks.filter((itme1) =>
					media.some((item2) => item2.title === itme1.title)
				);
			} catch (error) {
				console.error('Error fetching media data:', error.message);
			}
		}
	}
	let media = new Media();

	onMount(() => {
		ready = true;
		window.addEventListener('keydown', handleKeyDown);
	});
	onDestroy(() => {
		window.removeEventListener('keydown', handleKeyDown);
	});
	function handleKeyDown(event) {
		switch (event.key) {
			case 'Enter':
				tracks = [...tracks, media.mediaData[media.cursorAt]];
				presentIndicies.push(media.cursorAt);
				mediaList = media.mediaData;
				persistCursor = media.cursorAt;
				currentPlaylist.savePlaylist();
				media = new Media();
				break;

			case 'ArrowUp':
				if (media.cursorAt > 0) {
					if (presentIndicies.includes(media.cursorAt - 1)) {
						media.cursorAt -= 2;
						break;
					}
					media.cursorAt--;
				}
				break;

			case 'ArrowDown':
				if (media.cursorAt < mediaList.length - 1) {
					if (presentIndicies.includes(media.cursorAt + 1)) {
						media.cursorAt += 2;
						break;
					}
					media.cursorAt++;
				}
				break;

			case 'Escape':
				openSongList = false;
				currentPlaylist.pause = false;
				break;

			default:
				break;
		}
	}

	function inPlayList(song, idx) {
		let i;
		for (i = 0; i < presentTracks.length; i++) {
			if (presentTracks[i].title === song.title) {
				if (!presentIndicies.includes(idx)) {
					presentIndicies.push(idx);
				}

				return true;
			}
		}
	}
</script>

{#if ready && openSongList}
	<div
		class="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50 z-50"
	>
		<div class="flex items-center justify-center">
			<!-- colored container -->
			<div class="card items-start flex flex-col">
				<div class="w-[90%] h-[90%] mt-20 rounded-md">
					{#if mediaList}
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
									{#each mediaList as song, idx}
										<tr
											class="h-8 m-auto text-sm"
											class:active={media.cursorAt === idx}
											class:item={media.cursorAt !== idx}
										>
											{#if media.cursorAt === idx}
												<td class="py-1 text-nowrap align-top pr-2">&gt;</td>
											{:else}
												<td class="py-1 text-nowrap align-top"></td>
											{/if}

											{#if idx === media.selection}
												<td class="selected pr-3 py-2 text-nowrap align-top text-left"
													>{song.artist}</td
												>
												<td class="selected py-1 text-nowrap align-top text-left">{song.title}</td>
											{:else}
												<td
													class="pr-3 py-1 text-left text-nowrap align-top {inPlayList(song, idx)
														? 'present'
														: ''}">{song.artist}</td
												>
												<td
													class="py-1 text-nowrap align-top text-left {inPlayList(song, idx)
														? 'present'
														: ''}">{song.title}</td
												>
											{/if}
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					{:else}
						<p class="text-white">Loading...</p>
					{/if}
				</div>
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
		--card-height: 500px;
		--card-width: calc(var(--card-height) * 1.2);
	}

	.card {
		background: #191c29;
		width: 700px;
		height: 800px;
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
	.present {
		color: #4d4e56;
	}

	.item {
		color: rgb(31, 112, 218);
	}
</style>
