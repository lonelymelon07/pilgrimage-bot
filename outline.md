# The Bot's Outline

### `;add <id> <score> [display name]`  
adds a new pilgrimage
- `<name>` - the pilgrimage ID which will be used in commands  
- `<score>` - how many points the pilgrimage is worth  
- `[display name]` - the pilgrimage's display name

### `;award <@user> <id>`  
awards a user with a pilgrimage
- `<@user>` - user
- `<name>` - the pilgrimage ID

### `;rm <id>`
removes a pilgrimage
 - `<id>` - pilgrimage ID

### `;revoke <@user> <id>`
revokes a user from a pilgrimage
*(args same as `;award`)*

### `;list [page]`
lists all pilgrimages
- `[page]` - the page num to use

### `;pilg [@user]`
lists all pilgrimages
- `[@user]` - the user to list the pilgrimages of (if empty defaults to self)

<br>

*`<required argument> [optional argument]`*