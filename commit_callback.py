# Mapping from original commit SHA-1 (bytes) to new, professional commit messages (bytes)
MAPPING = {
    b"9273c905d19e098aaac4e2c25dd8b4d9dd4ecabd": b"chore(branding): rebrand assets to Fitness Plus; update watermarks, captions, outro, configs, and references\n",
    b"7f2155ecc0818886bb831ecc41adbdfd798733a8": b"chore(branding): standardize brand naming to professional terminology\n",
    b"6568fe6ab8fac8e63b16ebfe8683cb2307590c03": b"feat(cleanup): implement retention to keep only the 3 most recent processed videos\n",
    b"bedb17164fbae7ba33b4f19ee4b354fe33dbf93b": b"chore(cleanup): remove processed and temporary video files\n",
    b"cde072b8d45b2a3cdbc2d8b4954f67cb20f5b984": b"feat(app): introduce web app for watermark processing; add .gitignore\n",
    b"13cd61baba91c2012e1fda7839f3b101ead2c842": b"chore(repo): add main application file\n",
    b"faeb18a1937998f7fd41ab276d5fb571e7024bd4": b"fix(server): address server startup/runtime issue\n",
    b"b1c0cd159377f35ce194f7c8a7a0b37bc019abc6": b"refactor(server): update server module implementation\n",
    b"9f68b7da7a7564d2052ec104ac79f0c19b62fe22": b"refactor(server): refine server module logic\n",
    b"da6388e76ebfd96500ec4529a973bcde3be40ebf": b"fix(server): resolve recurring initialization issue\n",
    b"3bb4392e32ff2ac2e4c3dcd99ba1f7bff84b7b9f": b"refactor(server): incremental server module improvements\n",
    b"2471bd1b051a62c6e0a4ba3c9d119364adcef6bf": b"refactor(server): additional server module updates\n",
    b"af638c7c3bacb90b9c7c9113d583a4c055373804": b"docs(readme): improve documentation and project overview\n",
    b"44e767640cc193b29e6dd7debd63c64124901d50": b"docs(readme): update usage instructions\n",
    b"ac33412edda3b05cc4d91574fe6ffbd442595ff9": b"chore(legal): add license file\n",
    b"f2858571566eefa70be9d267c4841b599394853e": b"docs(readme): refine documentation\n",
    b"66b0e5ad1167b4096aa559d10748d20f52968889": b"refactor(server): update server module\n",
    b"47a55a5477a7427f7d5d0430666bd786c537541a": b"feat(video): add outro support\n",
    b"b0a8d21723ab21f7d09f172e6e697786068b0020": b"chore(init): initial project files\n",
}


def commit_callback(commit):
    """git-filter-repo commit callback to replace commit messages by original id."""
    new_message = MAPPING.get(commit.original_id)
    if new_message is not None:
        commit.message = new_message