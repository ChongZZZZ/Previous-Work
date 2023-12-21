package maze.tile;

import java.io.IOException;
import java.util.EnumSet;
import java.util.Iterator;

import gamecore.GameEngine;
import gamecore.IUpdatable;
import gamecore.datastructures.grids.FixedSizeGrid;
import gamecore.datastructures.vectors.Vector2d;
import gamecore.datastructures.vectors.Vector2i;
import gamecore.gui.gamecomponents.AffineComponent;
import maze.tile.MazeTile.TileID;
import maze.tile.tiles.PlainTile;
import maze.tile.tiles.TeleportDestinationTile;
import maze.tile.tiles.TeleportStartTile;

/**
 * A 3x3 block of MazeTiles used to make maze generation easy.
 * @author Dawn Nye
 */
public class MazeBigTile extends AffineComponent implements IUpdatable
{
	/**
	 * Creates a 3x3 collection of maze tiles that require no additional parameters to construct.
	 * @param type The tile type. This constructor will only accept {@code PLAIN} and {@code TELEPORT_DESTINATION}. If it is not one of these, it will default to PLAIN.
	 * @param exits Each element of this set will provide an exit (and entrance) to this tile.
	 * @throws IOException Thrown if something goes wrong with sprite loading.
	 */
	public MazeBigTile(TileTypes type, EnumSet<Exit> exits, Vector2i pos) throws IOException
	{
		Tiles = new FixedSizeGrid<>(3,3);
		
		this.Pos= pos;
		
		if(type.equals(TileTypes.TELEPORT_DESTINATION)){
			Tiles.Set(new TeleportDestinationTile(), Middle);
		}
		else {
			Tiles.Set(new PlainTile(), Middle);
		}
		
		SetExit(exits);
		
		SetNormalCorner();
		
		SetNormalPath();
		
		
		return;
	}
	
	
	/**
	 * Creates a 3x3 collection of maze tiles that start
	 * @param type The tile type. This constructor will only accept {@code PLAIN} and {@code START}. If it is not one of these, it will default to PLAIN.
	 * @param exits Each element of this set will provide an exit (and entrance) to this tile.
	 * @throws IOException Thrown if something goes wrong with sprite loading.
	 */
	public MazeBigTile(EnumSet<Exit> exits, Vector2i pos) throws IOException
	{
		Tiles = new FixedSizeGrid<>(3,3);
		
		this.Pos= pos;
		
		Tiles.Set(new MazeTile(TileID.START,false,false), Middle);
		
		SetExit(exits);
		
		SetNormalCorner();
		
		SetNormalPath();
		
		
		return;
	}
	
	
	
	/**
	 * Creates a 3x3 collection of maze tiles that require a {@code Vector2d} to construct.
	 * @param type The tile type. This constructor will only accept {@code TELEPORTER}. If it is not one of these, it will default to PLAIN.
	 * @param exits The exits to the big tile.
	 * @param displacement The diplacement the teleporter does to the player.
	 * @throws IOException Thrown if something goes wrong with sprite loading.
	 */
	public MazeBigTile(TileTypes type, EnumSet<Exit> exits, Vector2d displacement, Vector2i pos) throws IOException
	{
		Tiles = new FixedSizeGrid<>(3,3);
		
		this.Pos=pos;
		
		if(type.equals(TileTypes.TELEPORTER)){
			Tiles.Set(new TeleportStartTile(displacement), Middle);
		}
		else {
			Tiles.Set(new PlainTile(), Middle);
		}
		
		SetExit(exits);
		
		SetNormalCorner();
		
		SetNormalPath();
		
	
		
		return;
	}
	
	/**
	 * Creates a 3x3 collection of maze tiles that require an {@code Exit} to construct.
	 * @param type The tile type. This constructor will only accept {@code EXIT}. If it is not one of these, it will default to PLAIN.
	 * @param exits The exits to the big tile. If this does not contain {@code true_exit}, it will be added to the set.
	 * @param true_exit The exit direction out of the maze.
	 * @throws IOException Thrown if something goes wrong with sprite loading.
	 */
	public MazeBigTile(TileTypes type, EnumSet<Exit> exits, Exit true_exit, Vector2i pos, int Width, int Height) throws IOException
	{
		Tiles = new FixedSizeGrid<>(3,3);
		
		this.Pos=pos;
		
		if(type.equals(TileTypes.EXIT)){
			Tiles.Set(new PlainTile(), Middle); //set exit
		}
		else {
			Tiles.Set(new PlainTile(), Middle);
		}
		
		SetExit(exits);
		
		SetExitWall(true_exit, Width, Height);
		
		SetNormalCorner();
		
		SetNormalPath();
		
		
		SetTrueExit(true_exit);
		
		
		
		return;
	}
	

	/**
	 * This function set all the image for the exits 
	 * @param exits The exits to the big tile. If this does not contain {@code true_exit}, it will be added to the set.
	 * @throws IOException Thrown if something goes wrong with sprite loading.
	 */
	public void SetExit(EnumSet<Exit> exits) throws IOException {

		Iterator<Exit> iter= exits.iterator();
		while(iter.hasNext()) {
			Exit temp= iter.next();
			if(temp.equals(Exit.RIGHT)) {
				Tiles.Set(new PlainTile(), Right);
			}
			else if(temp.equals(Exit.LEFT)) {
				Tiles.Set(new PlainTile(), Left);
			}
			else if (temp.equals(Exit.DOWN)) {
				Tiles.Set(new PlainTile(), Bottom);
			}
			else if (temp.equals(Exit.UP)) {
				Tiles.Set(new PlainTile(), Top);
			}	
		}

		return;
	}
	
	/**
	 * This function set the true exit by overlaying it on an exit
	 * @param true_exit The exit direction out of the maze.
	 * @throws IOException Thrown if something goes wrong with sprite loading
	 */
	public void SetTrueExit(Exit true_exit) throws IOException {

		if(true_exit.equals(Exit.RIGHT)) {
			Tiles.Set(new MazeTile(TileID.R_EXIT,false,false), Right);
		}
		else if(true_exit.equals(Exit.LEFT)) {
			Tiles.Set(new MazeTile(TileID.L_EXIT,false,false), Left);
		}
		else if (true_exit.equals(Exit.DOWN)) {
			Tiles.Set(new MazeTile(TileID.B_EXIT,false,false), Bottom);
		}
		else if (true_exit.equals(Exit.UP)) {		
			Tiles.Set(new MazeTile(TileID.T_EXIT,false,false), Top);
		}	

		return;
	}

	/**
	 * This function set the wall for 4 tiles(middletop, middlebottom, middleleft, and middleright)
	 * @throws IOException Thrown if something goes wrong with sprite loading
	 */
	public void SetNormalPath() throws IOException {
		if(Tiles.IsCellEmpty(Left)) {
			Tiles.Set(new MazeTile(TileID.L_STRAIGHT_WALL,true,false), Left);
		}
		if(Tiles.IsCellEmpty(Right)) {
			Tiles.Set(new MazeTile(TileID.R_STRAIGHT_WALL,true,false), Right);
		}
		if(Tiles.IsCellEmpty(Top)) {
			Tiles.Set(new MazeTile(TileID.T_STRAIGHT_WALL,true,false), Top);
		}
		if(Tiles.IsCellEmpty(Bottom)) {
			Tiles.Set(new MazeTile(TileID.B_STRAIGHT_WALL,true,false), Bottom);
		}
		
	}
	
	@SuppressWarnings("unlikely-arg-type")
	/**
	 * This function set the wall for 4 tiles at four corners
	 * @throws IOException if something goes wrong with sprite loading
	 */
	public void SetNormalCorner() throws IOException {
		MazeTile regular= new PlainTile();
	
		if(Tiles.IsCellEmpty(TopLeft)) {
			if(Tiles.IsCellOccupied(Left) && Tiles.IsCellOccupied(Top)) {
				Tiles.Set(new MazeTile(TileID.TL_BULGE_OUT,true,false),TopLeft);	
			}
			else if(Tiles.IsCellOccupied(Top)) {
				Tiles.Set(new MazeTile(TileID.L_STRAIGHT_WALL,true,false),TopLeft);	
			}
			else if (Tiles.IsCellOccupied(Left)) {
				Tiles.Set(new MazeTile(TileID.T_STRAIGHT_WALL,true,false),TopLeft);	
			}
			else {
				Tiles.Set(new MazeTile(TileID.TL_BULGE_IN,true,false),TopLeft);
			}
		}
		
		if(Tiles.IsCellEmpty(TopRight)) {
			if(Tiles.IsCellOccupied(Top) && Tiles.IsCellOccupied(Right)) {
				Tiles.Set(new MazeTile(TileID.TR_BULGE_OUT,true,false),TopRight);	
			}
			else if(Tiles.IsCellOccupied(Top)) {
				Tiles.Set(new MazeTile(TileID.R_STRAIGHT_WALL,true,false),TopRight);	
			}
			else if(Tiles.IsCellOccupied(Right)) {
				Tiles.Set(new MazeTile(TileID.T_STRAIGHT_WALL,true,false),TopRight);	
			}
			else {
				Tiles.Set(new MazeTile(TileID.TR_BULGE_IN,true,false),TopRight);
			}
		}
		
		if(Tiles.IsCellEmpty(BottomLeft)) {
			if(Tiles.IsCellOccupied(Bottom) && Tiles.IsCellOccupied(Left)) {
				Tiles.Set(new MazeTile(TileID.BL_BULGE_OUT,true,false),BottomLeft);	
			}
			else if(Tiles.IsCellOccupied(Bottom)) {
				Tiles.Set(new MazeTile(TileID.L_STRAIGHT_WALL,true,false),BottomLeft);	
			}
			else if(Tiles.IsCellOccupied(Left)) {
				Tiles.Set(new MazeTile(TileID.B_STRAIGHT_WALL,true,false),BottomLeft);	
			}
			else {
				Tiles.Set(new MazeTile(TileID.BL_BULGE_IN,true,false),BottomLeft);
			}
		}
		
		if(Tiles.IsCellEmpty(BottomRight)) {
			if(Tiles.IsCellOccupied(Bottom) && Tiles.IsCellOccupied(Right)) {
				Tiles.Set(new MazeTile(TileID.BR_BULGE_OUT,true,false),BottomRight);	
			}
			else if(Tiles.IsCellOccupied(Bottom)) {
				Tiles.Set(new MazeTile(TileID.R_STRAIGHT_WALL,true,false),BottomRight);
			}
			else if (Tiles.IsCellOccupied(Right)) {
				Tiles.Set(new MazeTile(TileID.B_STRAIGHT_WALL,true,false),BottomRight);	
			}
			else {
				Tiles.Set(new MazeTile(TileID.BR_BULGE_IN,true,false),BottomRight);
			}
			
		}
	}
	
	
	public void SetExitWall(Exit true_exit, int Width, int Height) throws IOException {
		if(true_exit.equals(Exit.RIGHT)) {
			if(this.Pos.X==(Width-1) && this.Pos.Y==0) {
				if(Tiles.IsCellOccupied(Bottom)) {
				Tiles.Set(new MazeTile(TileID.B_R_EXIT_WALL,true,false), BottomRight);}
			}
			else if(this.Pos.X==(Width-1)&& this.Pos.Y==(Height-1)) {
				if(Tiles.IsCellOccupied(Top)) {
				Tiles.Set(new MazeTile(TileID.T_R_EXIT_WALL,true,false), TopRight);}
			}
			else if (this.Pos.X==(Width-1)) {
				if(Tiles.IsCellOccupied(Top)) {
				Tiles.Set(new MazeTile(TileID.T_R_EXIT_WALL,true,false), TopRight);
				}
				if(Tiles.IsCellOccupied(Bottom)) {
				Tiles.Set(new MazeTile(TileID.B_R_EXIT_WALL,true,false), BottomRight);
				}
			}
		}
		else if(true_exit.equals(Exit.LEFT)) {
			if(this.Pos.X==0 && this.Pos.Y==0) {
				if(Tiles.IsCellOccupied(Bottom)) {
				Tiles.Set(new MazeTile(TileID.B_L_EXIT_WALL,true,false), BottomLeft);
				}	
			}
			else if(this.Pos.X==0 && this.Pos.Y==(Height-1)) {
				if(Tiles.IsCellOccupied(Top)) {
				Tiles.Set(new MazeTile(TileID.T_L_EXIT_WALL,true,false), TopLeft);
				}
			}
			else if (this.Pos.X==0) {
				if(Tiles.IsCellOccupied(Top)) {
				Tiles.Set(new MazeTile(TileID.T_L_EXIT_WALL,true,false), TopLeft);}
				if(Tiles.IsCellOccupied(Bottom)) {
				Tiles.Set(new MazeTile(TileID.B_L_EXIT_WALL,true,false), BottomLeft);}
			}
		}
		else if (true_exit.equals(Exit.DOWN)) {
			if(this.Pos.X==(Width-1) && this.Pos.Y==(Height-1)) {
				if(Tiles.IsCellOccupied(Left)) {
				Tiles.Set(new MazeTile(TileID.L_B_EXIT_WALL,true,false), BottomLeft);}
			}
			else if(this.Pos.X==0 && this.Pos.Y==(Height-1)) {
				if(Tiles.IsCellOccupied(Right)) {
				Tiles.Set(new MazeTile(TileID.R_B_EXIT_WALL,true,false), BottomRight);}
			}
			else if (this.Pos.Y==(Height-1)) {
				if(Tiles.IsCellOccupied(Right)) {
				Tiles.Set(new MazeTile(TileID.R_B_EXIT_WALL,true,false), BottomRight);}
				if(Tiles.IsCellOccupied(Left)) {
				Tiles.Set(new MazeTile(TileID.L_B_EXIT_WALL,true,false), BottomLeft);}
			}
		}
		else if (true_exit.equals(Exit.UP)) {		
			if(this.Pos.X==0 && this.Pos.Y==0) {
				if(Tiles.IsCellOccupied(Right)) {
				Tiles.Set(new MazeTile(TileID.R_T_EXIT_WALL,true,false), TopRight);}
			}
			else if(this.Pos.X==(Width-1) && this.Pos.Y==0) {
				if(Tiles.IsCellOccupied(Left)) {
				Tiles.Set(new MazeTile(TileID.L_T_EXIT_WALL,true,false), TopLeft);}
			}
			else if (this.Pos.Y==0) {
				if(Tiles.IsCellOccupied(Right)) {
				Tiles.Set(new MazeTile(TileID.R_T_EXIT_WALL,true,false), TopRight);}
				if(Tiles.IsCellOccupied(Left)) {
				Tiles.Set(new MazeTile(TileID.L_T_EXIT_WALL,true,false), TopLeft);}
			}
		}
	}
	
	/**
	 * Called before the first update to initialize the game component.
	 */
	public void Initialize()
	{
		Initialized = true;
		return;
	}
	
	/**
	 * Determines if this game component is initialized.
	 * @return Returns true if this game component is initialized and false otherwise.
	 */
	public boolean Initialized()
	{return Initialized;}
	
	/**
	 * Advances a game component by some time {@code delta}.
	 * @param delta The amount of time in milliseconds that has passed since the last update.
	 */
	public void Update(long delta)
	{return;}
	
	/**
	 * Called when the game component is removed from the game.
	 */
	public void Dispose()
	{
		// We'll just manually dispose of our children if we haven't gotten to them yet
		// Removal will be done in OnRemove if we need to (disposal at the end of the game's execution doesn't need to deal with removal)
		for(MazeTile t : Tiles.Items())
			if(!t.Disposed())
				t.Dispose();
		
		Disposed = true;
		return;
	}
	
	/**
	 * Determines if this game component has been disposed.
	 * @return Returns true if this game component has been disposed and false otherwise.
	 */
	public boolean Disposed()
	{return Disposed;}
	
	/**
	 * Called when the component is added to the game engine.
	 * This will occur before initialization when added for the first time.
	 */
	@Override public void OnAdd()
	{
		if(!InGame)
			for (int i=0; i<3; i++) {
				for(int j=0;j<3; j++) {
					Tiles.Get(j,i).Translate(new Vector2d(16*(j+3*Pos.X),16*(i+3*Pos.Y))); //unsure of the specific position;
					GameEngine.Game().AddComponent(Tiles.Get(new Vector2i(j,i)));
				}
			}
				
		
		InGame = true;
		return;
	}
	
	/**
	 * Called when the component is removed from the game engine.
	 * This will occur before disposal when removed with disposal.
	 */
	@Override public void OnRemove()
	{
		if(InGame)
			for(MazeTile t : Tiles.Items())
				GameEngine.Game().RemoveComponent(t);
		
		InGame = false;
		return;
	}
	
	/**
	 * The tiles comprising this maze tile.
	 */
	protected FixedSizeGrid<MazeTile> Tiles;
	
	/**
	 * If true, this tile has been initialized.
	 */
	protected boolean Initialized;
	
	/**
	 * If true, this tile has been disposed.
	 */
	protected boolean Disposed;
	
	/**
	 * If true, we're added into the game.
	 */
	protected boolean InGame;
	
	/**
	 * Position of this current big tile
	 */
	protected Vector2i Pos;
	
	/**
	 * Following are vectors corresponding to each cell of a 3*3 grid.
	 */
	protected final Vector2i Left= new Vector2i (0,1);
	
	protected final Vector2i Right= new Vector2i (2,1);
	
	protected final Vector2i Top= new Vector2i (1,0);
	
	protected final Vector2i Bottom= new Vector2i (1,2);
	 
	protected final Vector2i Middle= new Vector2i (1,1);
	
	protected final Vector2i TopLeft= new Vector2i(0,0);
	
	protected final Vector2i TopRight= new Vector2i(2,0);
	
	protected final Vector2i BottomLeft= new Vector2i(0,2);
	
	protected final Vector2i BottomRight= new Vector2i(2,2);
	
	
	
	
	
	/**
	 * Represents which directions you can exit (or enter) this tile.
	 * @author Dawn Nye
	 */
	public static enum Exit
	{
		UP,
		DOWN,
		LEFT,
		RIGHT
	}
	
	/**
	 * Designates a number of special tiles type for when constructors cannot otherwise reasonably destinguish between them.
	 * @author Dawn Nye
	 */
	public static enum TileTypes
	{
		PLAIN, // An ordinary center tile
		TELEPORT_DESTINATION, // A teleport destination tile
		START, // A start tile
		TELEPORTER, // A teleporter (requires a Vector2d)
		EXIT // An exit from the maze (requires an Exit)
	}
}