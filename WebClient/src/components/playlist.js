export class Playlist {
	constructor({ name, cursorAt }) {
		this.name = name;
		this.cursorAt = cursorAt;
		cursorAt += 1;
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
            console.log()
			// const saveEndpoint = `${url}/${this.name}/update`;
			// const options = {
			// 	method: 'PUT',
			// 	headers: {
			// 		'Content-Type': 'application/json'
			// 	},
			// 	body: JSON.stringify(data)
			// };
			// fetch(saveEndpoint, options)
			// 	.then((response) => {
			// 		if (!response.ok) {
			// 			console.log('response, ', response);
			// 			throw new Error('Network response was not ok');
			// 		}
			// 		return response.json();
			// 	})
			// 	.then((data) => {
			// 		console.log('Playlist saved successfully:', data);
			// 	})
			// 	.catch((error) => {
			// 		console.error('Error saving playlist:', error);
			// 	});
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
							let tracks = this.tracks;
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
			}
		};
		document.addEventListener('keydown', this.handleKeyEvent.bind(this));
	}
}
