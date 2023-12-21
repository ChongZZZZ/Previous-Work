package maze.tile;

import java.io.File;
import java.io.IOException;

import gamecore.GameEngine;
import gamecore.datastructures.CellRectangle;
import gamecore.datastructures.vectors.Vector2i;
import gamecore.gui.gamecomponents.ImageComponent;
import gamecore.sprites.SpriteSheet;
import maze.collision.CollisionEngine;
import maze.collision.ICollidable;

/**
 * The bare bones of what a maze tile should be.
 * This has no special properties
 * @author Dawn Nye
 */
public class MazeTile extends ImageComponent implements ICollidable
{
	/**
	 * Creates a new maze tile.
	 * @param sprite_id The index of the sprite in the tile sprite sheet.
	 * @param is_solid If true, this is a solid tile. This value should probably be false if it is a trigger.
	 * @param is_trigger If true, this is a trigger tile. This value should probably be false if it is solid.
	 * @throws IOException Thrown if something goes wrong with the sprite loading.
	 */
	protected MazeTile(TileID sprite_id, boolean is_solid, boolean is_trigger) throws IOException
	{
		super(SpriteSheet.LoadSprites(new File("assets/sprite sheets/Tiles.spritesheet")).GetSprite(sprite_id.ID));
		
		Solid = is_solid;
		Trigger = is_trigger;
		
		InGame = false;
		return;
	}
	
	/**
	 * Called when the component is added to the game engine.
	 * This will occur before initialization when added for the first time.
	 * Note also that this requires a subsequent call to the {@code CollisionEngine}'s {@code Flush} method to be properly added.
	 */
	@Override public void OnAdd()
	{
		super.OnAdd();
		
		if(InGame)
			return;
		
		InGame = true;
		
		// We don't want to clog our collision engine with garbage
		if(IsSolid() || IsTrigger())
			GameEngine.Game().<CollisionEngine>GetService(CollisionEngine.class).DelayAdd(this);
		
		return;
	}
	
	@Override public void OnRemove()
	{
		super.OnRemove();
		
		if(!InGame)
			return;
		
		InGame = false;
		
		if(IsSolid() || IsTrigger())
			GameEngine.Game().<CollisionEngine>GetService(CollisionEngine.class).Remove(this);
		
		return;
	}
	
	public CellRectangle GetBoundary()
	{return new CellRectangle(new Vector2i(GetPosition(true)),16,16);}
	
	public boolean IsStatic()
	{return true;}
	
	public boolean IsSolid()
	{return Solid;}
	
	public boolean IsTrigger()
	{return Trigger;}
	
	/**
	 * If true, this is a solid tile.
	 */
	protected boolean Solid;
	
	/**
	 * If true, this is a triggerable tile.
	 */
	protected boolean Trigger;
	
	/**
	 * If true, we're already in the game.
	 */
	protected boolean InGame;
	
	/**
	 * Sprite index IDs in the tile sprite sheet.
	 * @author Dawn Nye
	 */
	public static enum TileID
	{
		BL_BULGE_IN(0),
		BR_BULGE_IN(1),
		TL_BULGE_IN(2),
		TR_BULGE_IN(3),
		BR_BULGE_OUT(4),
		BL_BULGE_OUT(5),
		TL_BULGE_OUT(6),
		TR_BULGE_OUT(7),
		T_STRAIGHT_WALL(8),
		B_STRAIGHT_WALL(9),
		R_STRAIGHT_WALL(10),
		L_STRAIGHT_WALL(11),
		L_B_EXIT_WALL(12),
		B_EXIT(13),
		R_B_EXIT_WALL(14),
		L_T_EXIT_WALL(16),
		T_EXIT(17),
		R_T_EXIT_WALL(18),
		T_R_EXIT_WALL(20),
		R_EXIT(21),
		B_R_EXIT_WALL(22),
		T_L_EXIT_WALL(15),
		L_EXIT(19),
		B_L_EXIT_WALL(23),
		PLAIN(24),
		PLAIN_WALL(25),
		START(26),
		NOTHING(27);
		
		private TileID(int id)
		{
			ID = id;
			return;
		}
		
		/**
		 * The index in the sprite sheet for this type type.
		 */
		public final int ID;
	}
}
