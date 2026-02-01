# Ethiopia Data Science Workshop 2026

**Data Sciences for Modeling and Health Technology Assessment**

WISE Project Training Workshop | Addis Ababa University | February 2-7, 2026

## Overview

This repository contains the course materials for the WISE Project training workshop on data science methods for health technology assessment and supply chain modeling.

## Workshop Structure

- **Days 1-3**: Data Science Foundations, Machine Learning, Integration (Sylvia & Ozawa)
- **Day 4**: Agent-Based Modeling Deep Dive (Ozawa)
- **Days 5-6**: Health Technology Assessment (Gebretekle)

## Technology Stack

- **Website**: Quarto
- **Coding**: Google Colab (Python)
- **Deployment**: GitHub Pages with password protection

## Local Development

```bash
# Clone the repository
git clone https://github.com/sysylvia/ethiopia-ds-workshop-2026.git
cd ethiopia-ds-workshop-2026

# Preview the website
quarto preview
```

## Deployment

The site is automatically deployed to GitHub Pages on push to main. Password protection is handled via staticrypt.

To deploy:
1. Ensure `WORKSHOP_PASSWORD` secret is set in repository settings
2. Push to main branch
3. GitHub Actions will build and deploy

## License

Materials are provided for educational purposes as part of the WISE Project, funded by the Gates Grand Challenges Award.

## Contact

- Sean Sylvia (ssylvia@unc.edu)
- Sachiko Ozawa
