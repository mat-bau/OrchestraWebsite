class GalleryLoader {
    constructor(configPath = 'frontend/js/gallery-config.json') {
        this.configPath = configPath;
        this.config = null;
    }

    async init() {
        try {
            const response = await fetch(this.configPath);
            this.config = await response.json();
            this.generateGallery();
        } catch (error) {
            console.error('Erreur lors du chargement de la configuration:', error);
        }
    }

    generateGallery() {
        const filterContainer = document.querySelector('.filter-links.filterable-nav');
        const galleryContainer = document.querySelector('.filterable-items');

        if (filterContainer && galleryContainer) {
            // Garder le select mobile
            const selectHTML = filterContainer.querySelector('select')?.outerHTML || '';
            
            // Générer les boutons de filtre
            const buttons = Object.keys(this.config).map(key => 
                `<a href="#" data-filter=".${key}">${this.config[key].title}</a>`
            ).join('\n');
            
            filterContainer.innerHTML = selectHTML + buttons + '\n<a href="#" data-filter="*">Show all</a>';
            
            // Générer les images
            galleryContainer.innerHTML = this.generateImages();
            
            // Réinitialiser Isotope si présent
            if (typeof $ !== 'undefined' && $.fn.isotope) {
                $('.filterable-items').isotope('reloadItems');
            }
        }
    }

    generateImages() {
        let html = '';
        
        Object.keys(this.config).forEach(categoryKey => {
            const category = this.config[categoryKey];
            const images = this.getImagesForCategory(category);
            
            images.forEach(img => {
                html += `
                    <div class="filterable-item ${categoryKey}">
                        <a href="${category.folder}/${img.src}">
                            <figure>
                                <img src="${category.folder}/${img.thumb}" alt="gallery ${categoryKey}">
                            </figure>
                        </a>
                    </div>
                `;
            });
        });
        
        return html;
    }

    getImagesForCategory(category) {
        const images = [];
        
        // Mode liste manuelle
        if (category.images) {
            return category.images.map(img => ({ src: img, thumb: img }));
        }
        
        // Mode avec numéros spécifiques
        if (category.numbers) {
            category.numbers.forEach(num => {
                const filename = category.pattern.replace('{i}', num);
                images.push({ src: filename, thumb: filename });
            });
            return images;
        }
        
        // Mode avec plages multiples par extension
        if (category.ranges) {
            Object.keys(category.ranges).forEach(ext => {
                const range = category.ranges[ext];
                for (let i = range.start; i <= range.end; i++) {
                    const src = category.pattern.replace('{i}', i).replace('{ext}', ext);
                    const thumb = category.thumbPattern ? 
                        category.thumbPattern.replace('{i}', i).replace('{ext}', ext) : 
                        src;
                    images.push({ src, thumb });
                }
            });
            return images;
        }
        
        // Mode avec plage simple
        if (category.range) {
            for (let i = category.range.start; i <= category.range.end; i++) {
                const src = category.pattern.replace('{i}', i);
                const thumb = category.thumbPattern ? 
                    category.thumbPattern.replace('{i}', i) : 
                    src;
                images.push({ src, thumb });
            }
        }
        
        return images;
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    const gallery = new GalleryLoader();
    gallery.init();
});

// Configuration de la galerie - à mettre dans un fichier séparé ou en haut de ton script
const GALLERY_CONFIG = {
    concert2024: {
        folder: '../../images/concert2024',
        title: 'Concert 2024',
        extensions: ['jpg', 'jpeg', 'png'],
        count: 64 // nombre de photos, ou null pour auto-détection
    },
    concert2023: {
        folder: '../../images/concert2023',
        title: 'Concert 2023',
        extensions: ['jpg', 'jpeg', 'png'],
        count: 50
    },
    concert2022: {
        folder: '../../images/concert_2022',
        title: 'Concert 2022',
        extensions: ['jpeg'],
        count: 23,
        prefix: 'Orchestra_kot_nov2022_' // préfixe spécial pour 2022
    },
    concert2021: {
        folder: '../../images/concert2021',
        title: 'Concert 2021',
        extensions: ['jpeg'],
        count: 41,
        prefix: 'concert2021('
    },
    concert2019: {
        folder: '../../images/Concert2019',
        title: 'Concert 2019',
        extensions: ['jpeg'],
        count: 25,
        prefix: 'Concert2019_'
    },
    leconcert: {
        folder: '../../images/concert',
        title: 'Concert 2018',
        extensions: ['png'],
        count: 67,
        prefix: 'concert',
        hasSmallVersion: true // pour les images avec version small
    },
    band: {
        folder: '../../images/lequipe',
        title: "L'équipe",
        images: ['lequipe6.jpg', 'lequipe4.jpg', 'lequipe5.jpg', 'lequipe2.jpg', 'lequipe1.jpg', 'lequipe3.jpg']
    },
    omps: {
        folder: '../../images',
        title: 'OMPs',
        images: [] // etc... ou count: 51
    }
};

function generateGalleryHTML() {
    let html = '';
    
    Object.keys(GALLERY_CONFIG).forEach(categoryKey => {
        const category = GALLERY_CONFIG[categoryKey];
        
        if (category.images) {
            // Mode manuel : liste d'images spécifique
            category.images.forEach(image => {
                html += createImageHTML(categoryKey, category.folder, image, image);
            });
        } else {
            // Mode automatique : génération basée sur count/extensions
            generateImagesForCategory(categoryKey, category).forEach(imageInfo => {
                html += createImageHTML(categoryKey, category.folder, imageInfo.src, imageInfo.thumb);
            });
        }
    });
    
    return html;
}

function generateImagesForCategory(categoryKey, category) {
    const images = [];
    const { folder, count, extensions, prefix, hasSmallVersion } = category;
    
    if (category.prefix === 'concert2021(') {
        // Cas spécial pour 2021 avec parenthèses
        for (let i = 9; i <= count; i++) {
            extensions.forEach(ext => {
                const filename = `concert2021(${i}).${ext}`;
                images.push({ src: filename, thumb: filename });
            });
        }
    } else if (prefix === 'Orchestra_kot_nov2022_') {
        // Cas spécial pour 2022
        const numbers = ['001', '005', '010', '015', '019', '020', '025', '030', '035', '040', '045', '050', '055', '060', '065', '070', '075', '080', '085', '088', '090', '095', '100'];
        numbers.forEach(num => {
            const filename = `${prefix}${num}.jpeg`;
            images.push({ src: filename, thumb: filename });
        });
    } else if (prefix === 'Concert2019_') {
        // Cas spécial pour 2019 avec numéros spécifiques
        const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24];
        numbers.forEach(num => {
            const filename = `${prefix}${num}.jpeg`;
            images.push({ src: filename, thumb: filename });
        });
    } else if (hasSmallVersion) {
        // Cas spécial pour 2018 avec versions 
        for (let i = 1; i <= count; i++) {
            const filename = `${prefix}${i}.png`;
            const thumbname = `${prefix}${i}small.png`;
            images.push({ src: filename, thumb: thumbname });
        }
    } else {
        // Cas standard : Photo (1), Photo (2), etc.
        for (let i = 1; i <= count; i++) {
            extensions.forEach(ext => {
                const filename = `Photo (${i}).${ext}`;
                images.push({ src: filename, thumb: filename });
            });
        }
    }
    
    return images;
}

function createImageHTML(category, folder, src, thumb) {
    return `
        <div class="filterable-item ${category}">
            <a href="${folder}/${src}">
                <figure>
                    <img src="${folder}/${thumb}" alt="gallery ${category}">
                </figure>
            </a>
        </div>
    `;
}

function generateFilterButtons() {
    const buttons = Object.keys(GALLERY_CONFIG).map(key => {
        const category = GALLERY_CONFIG[key];
        return `<a href="#" data-filter=".${key}">${category.title}</a>`;
    }).join('\n');
    
    return buttons + '\n<a href="#" data-filter="*">Show all</a>';
}

// Fonction d'initialisation à appeler au chargement de la page
function initializeGallery() {
    // Générer les boutons de filtre
    const filterContainer = document.querySelector('.filter-links.filterable-nav');
    if (filterContainer) {
        // Garder le select mobile et ajouter les boutons
        const selectHTML = filterContainer.querySelector('select').outerHTML;
        filterContainer.innerHTML = selectHTML + generateFilterButtons();
    }
    
    // Générer les images
    const galleryContainer = document.querySelector('.filterable-items');
    if (galleryContainer) {
        galleryContainer.innerHTML = generateGalleryHTML();
    }
    
    // Réinitialiser le plugin de filtrage si nécessaire
    if (typeof $ !== 'undefined' && $.fn.isotope) {
        $('.filterable-items').isotope('reloadItems');
    }
}

// Appeler au chargement de la page
document.addEventListener('DOMContentLoaded', initializeGallery);