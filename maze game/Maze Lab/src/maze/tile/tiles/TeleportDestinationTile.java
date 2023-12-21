package maze.tile.tiles;

import java.io.File;
import java.io.IOException;

import gamecore.GameEngine;
import gamecore.gui.gamecomponents.AnimatedComponent;
import gamecore.sprites.Animation;
import maze.tile.MazeTile;

/**
 * An outbound teleportaiton tile.
 * @author Dawn Nye
 */
public class TeleportDestinationTile extends MazeTile
{
	/**
	 * Creates a new teleport destination tile.
	 * @throws IOException Thrown if something goes wrong with the sprite loading.
	 */
	public TeleportDestinationTile() throws IOException
	{
		super(TileID.PLAIN,false,false);
		
		TeleporterDestination = new AnimatedComponent(new Animation(new File("assets/animations/Destination Teleport.animation")));
		TeleporterDestination.SetParent(this);
		
		return;
	}
	
	public void Dispose()
	{
		// We'll just manually dispose of our children if we haven't gotten to them yet
		// Removal will be done in OnRemove if we need to (disposal at the end of the game's execution doesn't need to deal with removal)
		if(!TeleporterDestination.Disposed())
			TeleporterDestination.Dispose();
		
		super.Dispose();
		return;
	}
	
	@Override public void OnAdd()
	{
		if(InGame)
			return;
		
		super.OnAdd();
		
		// Add the teleporter after this component so it gets drawn on top of it
		GameEngine.Game().AddComponent(TeleporterDestination,GameEngine.Game().IndexOfComponent(this));
		
		return;
	}
	
	@Override public void OnRemove()
	{
		if(!InGame)
			return;
		
		super.OnRemove();
		GameEngine.Game().RemoveComponent(TeleporterDestination);
		
		return;
	}
	
	/**
	 * The animation to play for the teleporter.
	 */
	protected AnimatedComponent TeleporterDestination;
}