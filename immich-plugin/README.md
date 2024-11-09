1. Install https://www.tampermonkey.net/ extension
2. Add a new script. In the script, replace the URL with your host:

```
// @match        https://IMMICH INSTANCE/photos/*
// @match        https://IMMICH INSTANCE/folders/photos/*
```

3. Configure album ids that you want to support:

```
const albumShortcuts = {
    'z': 'b395bdc8-7e03-4e3b-8e33-681e3bb5e859', // lower case adds to album, upper case removes from album
};
```

Replace the guid with guids of the actual albums

