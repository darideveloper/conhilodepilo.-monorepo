# Design: Landing Gallery Image Update

## Asset Organization
The new images are located at `/home/daridev/Downloads/temp-images/tinified/`.
They are named `gallery-1.webp` through `gallery-8.webp`.

### Renaming Mapping
| Source File | Destination File |
| :--- | :--- |
| `gallery-1.webp` | `landing/src/assets/images/gallery/gallery-01.webp` |
| `gallery-2.webp` | `landing/src/assets/images/gallery/gallery-02.webp` |
| `gallery-3.webp` | `landing/src/assets/images/gallery/gallery-03.webp` |
| `gallery-4.webp` | `landing/src/assets/images/gallery/gallery-04.webp` |
| `gallery-5.webp` | `landing/src/assets/images/gallery/gallery-05.webp` |
| `gallery-6.webp` | `landing/src/assets/images/gallery/gallery-06.webp` |
| `gallery-7.webp` | `landing/src/assets/images/gallery/gallery-07.webp` |
| `gallery-8.webp` | `landing/src/assets/images/gallery/gallery-08.webp` |

## Component Update
The `Gallery.astro` component imports these images as variables (`img1`, `img2`, etc.).
The import statements will be updated to point to the new `.webp` files.
The `alt` texts in `defaultGalleryData` should be reviewed during implementation to ensure they still accurately describe the new images.

```astro
// From
import img1 from "../../assets/images/gallery/gallery-01.jpg";
// To
import img1 from "../../assets/images/gallery/gallery-01.webp";
```

## Migration Steps
1. Copy new images to the target directory with the new names.
2. Update the Astro component.
3. Delete the old JPG images.
4. Verify build.
