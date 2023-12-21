package maze.tile.tiles;

import java.io.IOException;

import maze.tile.MazeTile;

/**
 * Creates a plain tile for the maze.
 * @author Dawn Nye
 */
public class PlainTile extends MazeTile
{
	/**
	 * Creates a plain tile for the maze.
	 * @throws IOException Thrown if something goes wrong while loading sprites.
	 */
	public PlainTile() throws IOException
	{
		super(TileID.PLAIN,false,false);
		return;
	}
}