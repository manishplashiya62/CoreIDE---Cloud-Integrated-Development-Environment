// Treeview Manager for Web IDE

class FileTree {
    constructor(projectId, containerId) {
        this.projectId = projectId;
        this.container = document.getElementById(containerId);
        this.nodes = [];
        this.openFolders = new Set(); // Track expanded folder IDs
    }

    async load() {
        try {
            const res = await fetch(`/api/projects/${this.projectId}/tree`);
            if (!res.ok) throw new Error("Failed to load file explorer tree.");
            this.nodes = await res.json();
            this.render();
        } catch (e) {
            showToast(e.message, 'danger');
        }
    }

    render() {
        this.container.innerHTML = '';
        
        // Separate root nodes and child nodes
        const rootNodes = this.nodes.filter(n => !n.parent_id);
        const childrenMap = {};
        this.nodes.forEach(n => {
            if (n.parent_id) {
                if (!childrenMap[n.parent_id]) childrenMap[n.parent_id] = [];
                childrenMap[n.parent_id].push(n);
            }
        });

        // Sort: Folders first, then alphabetically
        const sortNodes = (arr) => {
            return arr.sort((a, b) => {
                if (a.is_folder !== b.is_folder) {
                    return a.is_folder ? -1 : 1;
                }
                return a.name.localeCompare(b.name);
            });
        };

        const buildDOM = (nodeList, parentElement) => {
            sortNodes(nodeList).forEach(node => {
                const li = document.createElement('li');
                li.style.listStyle = 'none';
                
                const nodeDiv = document.createElement('div');
                nodeDiv.className = `tree-node ${window.activeFileId === node.id ? 'active' : ''}`;
                nodeDiv.dataset.id = node.id;
                
                // Icon
                const iconSpan = document.createElement('span');
                iconSpan.className = 'tree-node-icon';
                if (node.is_folder) {
                    const isExpanded = this.openFolders.has(node.id);
                    iconSpan.innerHTML = isExpanded ? '📂' : '📁';
                } else {
                    iconSpan.innerHTML = this.getFileIcon(node.language);
                }
                
                // Name
                const nameSpan = document.createElement('span');
                nameSpan.className = 'tree-node-name';
                nameSpan.innerText = node.name;
                
                nodeDiv.appendChild(iconSpan);
                nodeDiv.appendChild(nameSpan);
                
                // Actions (Rename, Delete, Add inside Folder)
                const actionsDiv = document.createElement('div');
                actionsDiv.className = 'tree-node-actions';
                
                if (node.is_folder) {
                    const addFileBtn = document.createElement('button');
                    addFileBtn.innerHTML = '📄';
                    addFileBtn.title = 'New File';
                    addFileBtn.onclick = (e) => {
                        e.stopPropagation();
                        this.promptCreate(node.id, false);
                    };
                    actionsDiv.appendChild(addFileBtn);
                }
                
                const renameBtn = document.createElement('button');
                renameBtn.innerHTML = '✏️';
                renameBtn.title = 'Rename';
                renameBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.promptRename(node.id, node.name);
                };
                
                const deleteBtn = document.createElement('button');
                deleteBtn.innerHTML = '🗑️';
                deleteBtn.title = 'Delete';
                deleteBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.confirmDelete(node.id, node.name);
                };
                
                actionsDiv.appendChild(renameBtn);
                actionsDiv.appendChild(deleteBtn);
                nodeDiv.appendChild(actionsDiv);
                
                li.appendChild(nodeDiv);
                
                // Click handler
                nodeDiv.onclick = (e) => {
                    if (node.is_folder) {
                        if (this.openFolders.has(node.id)) {
                            this.openFolders.delete(node.id);
                        } else {
                            this.openFolders.add(node.id);
                        }
                        this.render();
                    } else {
                        if (window.openFileInEditor) {
                            window.openFileInEditor(node.id, node.name, node.language);
                        }
                        document.querySelectorAll('.tree-node').forEach(el => el.classList.remove('active'));
                        nodeDiv.classList.add('active');
                    }
                };
                
                parentElement.appendChild(li);
                
                // Draw children if expanded
                if (node.is_folder && this.openFolders.has(node.id)) {
                    const childrenUl = document.createElement('ul');
                    childrenUl.className = 'folder-children';
                    li.appendChild(childrenUl);
                    
                    const children = childrenMap[node.id] || [];
                    buildDOM(children, childrenUl);
                }
            });
        };
        
        buildDOM(rootNodes, this.container);
    }
    
    getFileIcon(lang) {
        switch (lang) {
            case 'python': return '🐍';
            case 'javascript': return '🟨';
            case 'c': return '🔵';
            case 'cpp': return '🔷';
            case 'java': return '☕';
            case 'html': return '🌐';
            case 'css': return '🎨';
            default: return '📄';
        }
    }

    async promptCreate(parentId = null, isFolder = false) {
        const type = isFolder ? "Folder" : "File";
        const name = prompt(`Enter ${type} Name:`);
        if (!name || !name.trim()) return;
        
        try {
            const res = await fetch(`/api/projects/${this.projectId}/files`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, is_folder: isFolder, parent_id: parentId })
            });
            if (!res.ok) throw new Error(`Failed to create ${type}`);
            showToast(`${type} created successfully!`, 'success');
            
            if (parentId) {
                this.openFolders.add(parentId);
            }
            this.load();
        } catch (e) {
            showToast(e.message, 'danger');
        }
    }

    async promptRename(nodeId, currentName) {
        const name = prompt(`Enter new name:`, currentName);
        if (!name || name.trim() === currentName) return;
        
        try {
            const res = await fetch(`/api/files/${nodeId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            if (!res.ok) throw new Error("Rename failed.");
            showToast("Renamed successfully!", "success");
            this.load();
            if (window.updateTabName) {
                window.updateTabName(nodeId, name);
            }
        } catch (e) {
            showToast(e.message, 'danger');
        }
    }

    async confirmDelete(nodeId, name) {
        if (!confirm(`Are you sure you want to delete "${name}"?`)) return;
        
        try {
            const res = await fetch(`/api/files/${nodeId}`, { method: 'DELETE' });
            if (!res.ok) throw new Error("Delete failed.");
            showToast("Deleted successfully!", "success");
            this.load();
            if (window.closeTab) {
                window.closeTab(nodeId);
            }
        } catch (e) {
            showToast(e.message, 'danger');
        }
    }
}
