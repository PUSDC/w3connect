## BBS Post JD

The tool to post JD on BBS using tool `w3connect`.

Steps:

    1. Create a post with staking

    2. Edit a post and make it active on BBS

    3. Verify the post at https://bbs.w3connect.org/post/<post_id>.md


Create a post with staking on BBS (HTTP POST)
```bash
curl http://127.0.0.1:5333/bbs/create_post
```
Parameters:

    No parameters required.


Edit a post and make it active on BBS (HTTP POST)
```bash
curl http://127.0.0.1:5333/bbs/edit_post
```

Parameters:

    post_id: The id of the post.

    title: The title of the post.

    content: The content of the post.

    category: The category of the post. Should be `jd` by default.

    live: Boolean, whether the post is active. Default is False.