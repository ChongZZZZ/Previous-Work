package maze;

import java.io.File;

import gamecore.GameEngine;
import gamecore.datastructures.CellRectangle;
import gamecore.datastructures.vectors.Vector2d;
import gamecore.datastructures.vectors.Vector2i;
import gamecore.gui.gamecomponents.ImageComponent;
import gamecore.input.InputManager;
import maze.collision.CollisionEngine;
import maze.collision.ICollidable;

/**
 * A very simple player capable of moving around
 * @author Dawn Nye
 */
public class Player extends ImageComponent implements ICollidable
{
	/**
	 * Creates a new player.
	 */
	public Player()
	{
		super(new File("assets/images/Player.png"));
		
		Frozen = false;
		InGame = false;
		
		return;
	}
	
	/**
	 * Advances a game component by some time {@code delta}.
	 * @param delta The amount of time in milliseconds that has passed since the last update.
	 */
	public void Update(long delta)
	{
		//update the situation of the player
		if(IsFrozen()) {
			return;
		}
		
		InputManager Input = GameEngine.Game().<InputManager>GetService(InputManager.class);
		
		//linking all the keyboard to input
		if(Input.GracelessInputSatisfied("Left")) {
			Translate(Vector2i.LEFT.Multiply(Speed));
		}
		if(Input.GracelessInputSatisfied("Right")) {
			Translate(Vector2i.RIGHT.Multiply(Speed));
		}
		if(Input.GracelessInputSatisfied("Up")) {
			Translate(Vector2i.UP.Multiply(Speed));
		}
		if(Input.GracelessInputSatisfied("Down")) {
			Translate(Vector2i.DOWN.Multiply(Speed));
		}
		
		
		return;
	}
	
	@Override 
	/**
	 * Called when the component is added to the game engine.
	 * This will occur before initialization when added for the first time.
	 */
	public void OnAdd()
	{
		super.OnAdd();
		
		if(InGame)
			return;
		
		InGame = true;
		
		GameEngine.Game().<CollisionEngine>GetService(CollisionEngine.class).Add(this);
		return;
	}
	
	@Override 
	/**
	 * Called when the component is removed from the game engine.
	 * This will occur before disposal when removed with disposal.
	 */
	public void OnRemove()
	{
		super.OnRemove();
		
		if(!InGame)
			return;
		
		InGame = false;
		
		GameEngine.Game().<CollisionEngine>GetService(CollisionEngine.class).Remove(this);
		return;
	}
	
	/**
	 * Freezes the player to prevent them from moving.
	 */
	public void Freeze()
	{
		Frozen = true;
		return;
	}
	
	/**
	 * Allows the player to move if frozen.
	 */
	public void Unfreeze()
	{
		Frozen = false;
		return;
	}
	
	/**'
	 * Determines if the player is frozen.
	 */
	public boolean IsFrozen()
	{return Frozen;}
	
	@Override
	/**
	 * Obtains the velocity of this collidable object.
	 */
	public Vector2d Velocity()
	{return new Vector2d(delta_p);}
	
	/**
	 * Obtains the bounding box for this collidable.
	 */
	public CellRectangle GetBoundary()
	{return new CellRectangle(new Vector2i(GetPosition(true)),10,10);}
	
	/**
	 * Determines if this is a static object.
	 * Static objects do not move.
	 */
	public boolean IsStatic()
	{return false;}
	
	/**
	 * Determines if this tile is solid.
	 */
	public boolean IsSolid()
	{return true;}
	
	/**
	 * Determines if this tile is a trigger.
	 */
	public boolean IsTrigger()
	{return false;}
	
	/**
	 * The velocity of this player.
	 */
	protected Vector2i delta_p;
	
	/**
	 * If true, we're frozen and cannot move.
	 */
	protected boolean Frozen;
	
	/**
	 * If true, we're already in the game.
	 */
	protected boolean InGame;
	
	/**
	 * The speed of the player.
	 */
	public static final double Speed = 2.0;
}
