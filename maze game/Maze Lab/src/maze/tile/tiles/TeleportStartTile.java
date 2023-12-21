package maze.tile.tiles;

import java.io.File;
import java.io.IOException;

import gamecore.GameEngine;
import gamecore.datastructures.vectors.Vector2d;
import gamecore.gui.gamecomponents.AnimatedComponent;
import gamecore.input.InputManager;
import gamecore.observe.IObserver;
import gamecore.sprites.Animation;
import gamecore.time.TimePartition;
import gamecore.time.TimePartition.TimeEvent;
import maze.Player;
import maze.collision.ICollidable;
import maze.tile.MazeTile;

/**
 * An outbound teleportaiton tile.
 * @author Dawn Nye
 */
public class TeleportStartTile extends MazeTile implements IObserver<TimePartition.TimeEvent>
{
	/**
	 * Creates a new teleport destination tile.
	 * @throws IOException Thrown if something goes wrong with the sprite loading.
	 */
	public  TeleportStartTile(Vector2d displacement) throws IOException
	{
		super(TileID.PLAIN,false,true);
		
		this.displacement=displacement;
		
		Teleporter = new AnimatedComponent(new Animation(new File("assets/animations/Active Teleport.animation")));//adding the teleporter
		Teleporter.SetParent(this);
		
		Animation startanimate=new Animation(new File("assets/animations/Portal.animation"));//adding the portal animation
		startanimate.Subscribe(this);//knowing when it ends
		Start= new AnimatedComponent(startanimate);
		Start.SetParent(this);
		Start.Translate(-6.0, 0);//translate a little bit
		
		Animation endanimate=new Animation(new File("assets/animations/Reverse Portal.animation"));//adding reverse portal animation
		endanimate.Subscribe(this);//knowing when it ends
		
		End= new AnimatedComponent(endanimate);
		End.Translate(displacement);
		End.SetParent(this);
		End.Translate(-6.0, 0);//translate a little bit
		
		this.teleportstart=false;
		this.teleportend=false;
			
		return;
	}
	
	/**
	 * Called when this is a trigger and something collides with it.
	 * @param other The collidable object that bumped into this.
	 */
	public void Trigger(ICollidable other) {
		Player p= GameEngine.Game().GetService(Player.class);
		
		InputManager Input = GameEngine.Game().<InputManager>GetService(InputManager.class);
		
		if(Input.GracelessInputSatisfied("A")) {//trigger condition
			p.Freeze();//freeze the player
			GameEngine.Game().AddComponent(Start,0);
			this.Start.Play();//begin the first part of the animation
			this.teleportstart=true;
			
		}
	}
	
	@Override
	/**
	 * Called when an observation is made.
	 * @param event The observation.
	 */
	public void OnNext(TimeEvent event) {
		Player p= GameEngine.Game().GetService(Player.class);
		
		if(event.IsEndOfTime()) {
			if(this.teleportstart &&(!this.teleportend)) {//when the first part start and the second part does not start
				this.Start.Stop();//end the first part
				GameEngine.Game().RemoveComponent(Start);
				this.teleportstart=false;
				GameEngine.Game().AddComponent(End,0);
				this.End.Play(); //begin the second part 
				this.teleportend= true;
			}
			
			else if(this.teleportend &&(!this.teleportstart)) {
				this.End.Stop();//end the second part
				p.Translate(displacement);//translate the player
				GameEngine.Game().RemoveComponent(End);
				this.teleportend=false;
				p.Unfreeze();//unfreeze the player
			}
		}
	}

	@Override
	/**
	 * Called when an error occurs.
	 * @param e The observed error.
	 */
	public void OnError(Exception e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	/**
	 * Called when the observable has finished sending observations.
	 */
	public void OnCompleted() {
		// TODO Auto-generated method stub
		
	}
	
	/**
	 * Dispose the elements of the teleport
	 */
	public void Dispose()
	{
		// We'll just manually dispose of our children if we haven't gotten to them yet
		// Removal will be done in OnRemove if we need to (disposal at the end of the game's execution doesn't need to deal with removal)
		if(!Teleporter.Disposed())
			Teleporter.Dispose();
		
		super.Dispose();
		return;
	}
	
	@Override 
	/**
	 * Called when the component is added to the game engine.
	 * This will occur before initialization when added for the first time.
	 * Note also that this requires a subsequent call to the {@code CollisionEngine}'s {@code Flush} method to be properly added.
	 */
	public void OnAdd()
	{
		if(InGame)
			return;
		
		super.OnAdd();
		
		// Add the teleporter after this component so it gets drawn on top of it
		GameEngine.Game().AddComponent(Teleporter,GameEngine.Game().IndexOfComponent(this));
		
		return;
	}
	
	@Override
	/**
	 * Called when the component is removed from the game engine.
	 * This will occur before disposal when removed with disposal.
	 */
	public void OnRemove()
	{
		if(!InGame)
			return;
		
		super.OnRemove();
		GameEngine.Game().RemoveComponent(Teleporter);
		
		return;
	}
	
	/**
	 * The animation to play for the teleporter.
	 */
	protected AnimatedComponent Teleporter;
	
	/**
	 * The vector that shows the displacement of the player
	 */
	protected Vector2d displacement;
	
	/**
	 * The animation to play for portal
	 */
	protected AnimatedComponent Start;
	
	/**
	 * The animation to play for portal
	 */
	protected AnimatedComponent End;
	
	/**
	 * Determining whether the first part of the animation starts
	 */
	protected boolean teleportstart;
	

	/**
	 * Determining whether the second part of the animation starts
	 */
	protected boolean teleportend;


	
	
	
}
