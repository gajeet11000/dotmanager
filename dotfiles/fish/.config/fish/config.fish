if status is-interactive
    # Commands to run in interactive sessions can go here
end
set -U fish_greeting

# Utilities
alias c="clear"
alias ll="lsd -1 -hal --blocks permission,user,size,name --group-dirs=first"
alias lg="lazygit"
alias ld="lazydocker"
alias fontlist="fc-list : family | grep -v 'Noto' | sort -u | fzf"
alias task="go-task"

# Package Manager
alias search="yay -Ss "
alias install="yay -S --needed "
alias update="yay -Syu --noconfirm --needed --answerdiff None --answerclean NotInstalled && flatpak update -y"
alias remove="yay -Rnsd "


fish_vi_key_bindings
bind -M insert -m default ii backward-char force-repaint
bind -M insert \ef accept-autosuggestion

starship init fish | source

set -gx NVM_DIR "$HOME/.nvm"
set -gx PATH $HOME/.bin $PATH
set -gx PATH $HOME/.local/bin $PATH

function y
    set tmp (mktemp -t "yazi-cwd.XXXXXX")
    yazi $argv --cwd-file="$tmp"
    if read -z cwd <"$tmp"; and [ -n "$cwd" ]; and [ "$cwd" != "$PWD" ]
        builtin cd -- "$cwd"
    end
    rm -f -- "$tmp"
end
