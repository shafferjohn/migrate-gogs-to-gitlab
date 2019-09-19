# migrate gogs to gitlab

### Enviroment

- `python 3.7`

- `gogs 0.11.29.0727`

- `gitlab 12.2.5-ee`

### Usage

`python3 migrate.py`

if error, don't panic, debug it, delete `./tmp` directory, and run again.

### Q&A

occur the following error

```
error: RPC failed; HTTP 413 curl 22 
The requested URL returned error: 413 
fatal: the remote end hung up unexpectedly
```

you should enable gitlab large file storage (LFS) setting, if not working, check your nginx config, `client_max_body_size 100M;`


### Reference

- https://github.com/gogs/docs-api

- https://docs.gitlab.com/ee/api/users.html
