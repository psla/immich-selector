// ==UserScript==
// @name         Keyboard shortcut to add photos to Immich Album
// @namespace    http://psla.pl/
// @version      0.1
// @description  This plugin allows to define keyboard shortcuts that add/remove selected photos to an album
// @author       https://github.com/psla
// @match        https://IMMICH INSTANCE/photos/*
// @match        https://IMMICH INSTANCE/folders/photos/*
// @updateURL    https://github.com/psla/immich-selector/raw/immich-plugin/addToAlbum.user.js
// @downloadURL  https://github.com/psla/immich-selector/raw/immich-plugin/addToAlbum.user.js
// @grant        GM_setValue
// @grant        GM_getValue
// @require      https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js
// ==/UserScript==

// HashMap of shortcut characters to album names. Use lowercase letters.
const albumShortcuts = {
    'z': 'b395bdc8-7e03-4e3b-8e33-681e3bb5e859', // lower case adds to album, upper case removes from album
};


(function () {
    'use strict';

    document.addEventListener('keydown', function (e) {
            // Fetch the album name associated with the pressed key
            const targetAlbumId = albumShortcuts[e.key.toLowerCase()];
            if (targetAlbumId === undefined) {
                return;
            }
            var pictureId = window.location.pathname.split("/").pop();
            var request = { ids: [ pictureId ] };
            console.log(`Adding picture to album, ${JSON.stringify(request)}`);

        fetch(`/api/albums/${targetAlbumId}/assets`, {
            method: e.key.toLowerCase() === e.key ? "PUT" : "DELETE",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(request),
        }).then((response) => {
            // If the response is not 2xx, throw an error
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            // If the response is 200 OK, return the response in JSON format.
            return response.json();
        }).catch((error) => console.error("Fetch error:", error));
    }, true);

})();
