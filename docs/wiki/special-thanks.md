# 特别感谢

New API 的开发离不开社区的支持和贡献。在此特别感谢所有为项目提供帮助的个人和组织。

## 👨‍💻 开发贡献者

以下是所有为项目做出贡献的开发者列表。在此感谢他们的辛勤工作和创意！

!!! info "贡献者信息"
    以下贡献者数据从 [GitHub Contributors 页面](https://github.com/Calcium-Ion/new-api/graphs/contributors) 自动获取前100名。贡献度前三名分别以金、银、铜牌边框标识。如果您也想为项目做出贡献，欢迎提交 Pull Request。

{{ get_github_contributors() }}

<style>
.sponsor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.sponsor-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-color: #f8f9fa;
}

.sponsor-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.sponsor-card a {
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
}

.sponsor-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: contain;
  padding: 10px;
  background-color: white;
}

.sponsor-info {
  padding: 10px;
  text-align: center;
}

.sponsor-name {
  display: block;
  font-weight: bold;
  font-size: 1rem;
  margin-bottom: 5px;
}

.sponsor-tier {
  display: block;
  font-size: 0.8rem;
  color: #666;
}

[data-md-color-scheme="slate"] .sponsor-card {
  background-color: #2e303e;
}

[data-md-color-scheme="slate"] .sponsor-card img {
  background-color: #1e1e2e;
}

[data-md-color-scheme="slate"] .sponsor-tier {
  color: #aaa;
}
</style>
