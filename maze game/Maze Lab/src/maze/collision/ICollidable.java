package maze.collision;

import gamecore.datastructures.CellRectangle;
import gamecore.datastructures.vectors.Vector2d;

/**
 * Represents something that can be collided with.
 * @author Dawn Nye
 */
public interface ICollidable
{
	/**
	 * Translates this by {@code v}.
	 * @param v The translation.
	 * @throws NullPointerException Thrown is {@code v} is null.
	 */
	public void Translate(Vector2d v);
	
	/**
	 * Called when this is a trigger and something collides with it.
	 * @param other The collidable object that bumped into this.
	 */
	public default void Trigger(ICollidable other)
	{return;}
	
	/**
	 * Obtains the bounding box for this collidable.
	 */
	public CellRectangle GetBoundary();
	
	/**
	 * Obtains the velocity of this collidable object.
	 */
	public default Vector2d Velocity()
	{return Vector2d.ZERO;}
	
	/**
	 * Determines if this is a static object.
	 * Static objects do not move.
	 */
	public boolean IsStatic();
	
	/**
	 * Determines if this is a kinetic object.
	 * Kinetic objects move.
	 */
	public default boolean IsKinetic()
	{return !IsStatic();}
	
	/**
	 * Determines if this tile is solid.
	 */
	public boolean IsSolid();
	
	/**
	 * Determines if this tile is a trigger.
	 */
	public boolean IsTrigger();
}
