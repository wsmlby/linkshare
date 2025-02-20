# linkshare
linkshare is a docker native tool to share files from your local server with a signed url. 

It is useful when you want to share your file to people in the same network but don't want to give them full access to the server, and don't want to setup NFS/Samba permissions.

The idea is:
1. You create a signed link, with an optional expiration time for a file
2. You share this link
3. Anyone having this link can access this file(and of course, this file only), before it expire(if expiration is set).

## Deploy
The recommended way to deploy this is via docker

`docker run --name linkshare -d -e LINKSHARE_BASE_URI=<your_base_url> -v <host path>:/share/<targetname> -e LINKSHARE_KEY=<your_key> -p 25601:8000 wsmlby/linkshare:latest`

Or compose.yml
```
version: "3.8"

services:
  linkshare:
    image: wsmlby/linkshare:latest
    container_name: linkshare
    environment:
      - LINKSHARE_BASE_URI=<your_base_url>
      - LINKSHARE_KEY=<your_key>
    ports:
      - "25601:8000"
    volumes:
      - <host path1>:/share/<targetname1>
      - <host path2>:/share/<targetname2>
```

### Envs
1. LINKSHARE_BASE_PATH, default to /share, no need to change unless you want to use this outside of docker
2. LINKSHARE_KEY, secret to sign the url, please randomize it when you create your instance.
3. LINKSHARE_KEY_PATH, no need to set this unless you're not setting LINKSHARE_KEY and want to use a file for it. The file need to have less than open permission.
4. LINKSHARE_BASE_URI, the uri you want people to access your file from. It is recommended to use a reverse proxy, but it can be as simple as http://<your_host_name>:<your port>. This is only used to generate the signed url.



## To share a file
first, go inside the running docker instance
`docker exec -it linkshare /bin/bash`

then you can share a file with

`./linkshare.py share /share/<the file you want to share> [expiration_in_secs]`

The `expiration_in_secs` is optional, example:

```
root@a1a9749335db:/app# ./linkshare.py share /share/media/media1/Movie/BigBig.mp4 300
Sharing /share/media/media1/Movie/BigBig.mp4
https://share.example.net/media/media1/Movie/BigBig.mkv?sig=3325b61b9164614d9563de3377ed20f707b540366f74e7b52f9&exp=1740037513
```