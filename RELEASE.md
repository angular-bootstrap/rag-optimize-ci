# Release and Publish Guide

## 1. Create GitHub repository

Create an empty repo named `rag-optimize-ci` on GitHub.

## 2. Connect local repo and push

```bash
git remote add origin git@github.com:<your-username>/rag-optimize-ci.git
git push -u origin main
git push origin v0.1.0
```

## 3. Publish action as `@v1`

```bash
git tag -f v1
git push origin v1 --force
```

## 4. Optional package publish

If you decide to publish on PyPI later, add build/publish workflow and trusted publisher settings.
