from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from database import get_db, MovieModel
from schemas import MovieListResponseSchema

router = APIRouter()


# Write your code here
@router.get("/movies/", response_model=schemas.MovieListResponseSchema)
async def get_movies(page: int = Query(1, ge=1),
                     per_page: int = Query(default=10, ge=1, le=20),
                     db: AsyncSession = Depends(get_db)):
    movies = list(
        (await db.scalars(
            select(MovieModel).limit(per_page).offset((page - 1) * per_page)
        )).all()
    )
    total_items = await db.scalar(select(func.count()).select_from(MovieModel))

    if total_items % per_page != 0:
        total_pages = total_items // per_page + 1
    else:
        total_pages = total_items // per_page

    prev_page = None
    next_page = None

    if page > 1:
        prev_page = f"/theater/movies/?page={page - 1}&per_page={per_page}"
    if total_pages > page:
        next_page = f"/theater/movies/?page={page + 1}&per_page={per_page}"

    if not movies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No movies found.")
    return MovieListResponseSchema(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items
    )


@router.get("/movies/{movie_id}/", response_model=schemas.MovieDetailResponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await db.scalar(select(MovieModel).where(MovieModel.id == movie_id))

    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie with the given ID was not found.")
    return movie
