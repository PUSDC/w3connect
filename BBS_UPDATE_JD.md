## BBS Update JD

The tool to update JD on BBS using tool `w3connect`.

Steps:

    1. Edit a post and make it active on BBS

    2. Verify the post at https://bbs.w3connect.org/post/<post_id>.md


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
