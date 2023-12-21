package maze.collision;

import java.util.Iterator;

import gamecore.IUpdatable;
import gamecore.LINQ.LINQ;
import gamecore.datastructures.CellRectangle;
import gamecore.datastructures.ICollection;
import gamecore.datastructures.LinkedList;
import gamecore.datastructures.trees.AABBTree;
import gamecore.datastructures.vectors.Vector2d;

/**
 * Handles collisions.
 * @author Dawn Nye
 */
public class CollisionEngine implements IUpdatable, ICollection<ICollidable>
{
	/**
	 * Creates an empty collision engine.
	 */
	public CollisionEngine()
	{
		Kinetics = new LinkedList<ICollidable>();
		Statics = new AABBTree<ICollidable>(c -> c.GetBoundary());
		
		DelayedAdds = new LinkedList<ICollidable>();
		
		Initialized = false;
		Disposed = false;
		
		return;
	}
	
	/**
	 * Creates a collision engine.
	 * @param seed The initial elements to include in the collision engine.
	 */
	public CollisionEngine(Iterable<? extends ICollidable> seed)
	{
		Kinetics = new LinkedList<ICollidable>();
		Statics = new AABBTree<ICollidable>(c -> c.GetBoundary(),seed);
		
		DelayedAdds = new LinkedList<ICollidable>();
		
		Initialized = false;
		Disposed = false;
		
		return;
	}
	
	/**
	 * Called before the first update to initialize the game component.
	 */
	public void Initialize()
	{return;}
	
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
	{
		// We only care about kinetic-static collisions
		for(ICollidable c : Kinetics)
			for(ICollidable stat : Statics.Query(c))
			{
				// If we're a trigger, do that first in case magic happens
				if(stat.IsTrigger())
					stat.Trigger(c);
				
				// We don't do an else if here because maybe we trigger something by bumping into a solid
				if(stat.IsSolid())
					ResolveKineticStaticCollision(c,stat);
			}
		
		return;
	}
	
	/**
	 * Resolves a kinetic-static collision by pushing {@code kinetic} out to the nearest surface.
	 * @param kinetic The kinetic object.
	 * @param stat The static object.
	 * @throws NullPointerException Thrown if {@code kinetic} or {@code stat} is null. 
	 */
	protected void ResolveKineticStaticCollision(ICollidable kinetic, ICollidable stat)
	{
		
		CellRectangle player = kinetic.GetBoundary(); //get the boundary of player
		CellRectangle wall= stat.GetBoundary(); //get the boundary of wall
		CellRectangle overlay= player.Intersection(wall); //intersection
		
		if(overlay.IsEmpty()) {//this means that the player does not hit the wall
			return;
		}
		
		int posX;
		int posY;
		
		if(player.Center().X< wall.Center().X){ //the player hit from the left
			posX=1;
		}
		else {//the player hit from the right
			posX=-1;
		}
		
		if(player.Center().Y< wall.Center().Y){//the player hit from the top
			posY=1;
		}
		else { //the player hit from the bottom
			posY=-1;
		}

		if(overlay.Width()>overlay.Height()) {//the player hit horizontally
			kinetic.Translate(new Vector2d(0,1.1*(-posY)*overlay.Height()));
		}
		else {//the player hit vertically
			kinetic.Translate(new Vector2d(1.1*(-posX)*overlay.Width(),0));
		}
		
		return;
	}
	
	/**
	 * Called when the game component is removed from the game.
	 */
	public void Dispose()
	{
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
	 * Adds {@code c} to the collision engine.
	 * @param c The collidable object to add.
	 * @return Returns true if the add was successful and false otherwise.
	 * @implNote We do not prohibit duplicate values.
	 * @throws NullPointerException Thrown if {@code c} is null.
	 */
	public boolean Add(ICollidable c)
	{
		if(c.IsStatic())
			return Statics.Add(c);
		else
			return Kinetics.Add(c);
	}
	
	/**
	 * Adds {@code c} to the collision engine.
	 * However, it does not add this right away.
	 * It waits until a call to {@code Flush} is made.
	 * This is primarily useful for adding static objects to the collision engine before they have been moved to their final location.
	 * @param c The collidable object to add.
	 * @throws NullPointerException Thrown if {@code c} is null.
	 */
	public void DelayAdd(ICollidable c)
	{
		if(c == null)
			throw new NullPointerException();
		
		DelayedAdds.Add(c);
		return;
	}
	
	/**
	 * Flushes the delayed add list by adding all of them to the collision engine properly.
	 * @return Returns the number of items added successfully.
	 */
	public int Flush()
	{
		int ret = 0;
		
		for(ICollidable c : DelayedAdds)
			if(Add(c))
				ret++;
		
		DelayedAdds.Clear();
		return ret;
	}
	
	/**
	 * Removes {@code c} from the collision engine.
	 * @param c The collidable object to remove.
	 * @return Returns true if the remove was successful and false otherwise.
	 * @throws NullPointerException Thrown if {@code c} is null.
	 */
	public boolean Remove(ICollidable c)
	{
		if(c.IsStatic())
			return Statics.Remove(c);
		else
			return Kinetics.Remove(c);
	}
	
	@Override
	/**
	 * Determines if {@code t} is in the collection.
	 * @param t The item to search for.
	 * @return Returns true if the item is in the collection and false otherwise.
	 */
	public boolean Contains(ICollidable t)
	{return Kinetics.Contains(t) || Statics.Contains(t);}
	
	/**
	 * Determines the size of this collection.
	 * @return Returns the integer number of elements belonging to this collection.
	 */
	public int Count()
	{return Kinetics.Count() + Statics.Count();}
	
	/**
	 * Empties the collision engine of all collidable objects
	 */
	public void Clear()
	{
		Kinetics.Clear();
		Statics.Clear();
		
		return;
	}
	
	@Override
	public Iterator<ICollidable> iterator()
	{return LINQ.Concatenate(Kinetics,Statics).iterator();}
	
	/**
	 * The kinetic objects belonging to this collision engine.
	 */
	protected LinkedList<ICollidable> Kinetics;
	
	/**
	 * The static objects belonging to this collision engine.
	 */
	protected AABBTree<ICollidable> Statics;
	
	/**
	 * The collidable objects we are delaying to add until a Flush call.
	 */
	protected LinkedList<ICollidable> DelayedAdds;
	
	/**
	 * If true, this collision engine is initialized.
	 */
	protected boolean Initialized;
	
	/**
	 * If true, this collision engine is disposed.
	 */
	protected boolean Disposed;
}
