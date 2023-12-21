package maze;

import java.awt.event.KeyEvent;
import java.io.IOException;
import java.util.EnumSet;
import java.util.Random;

import gamecore.GameEngine;
import gamecore.datastructures.ArrayList;
import gamecore.datastructures.grids.FixedSizeGrid;
import gamecore.datastructures.queues.PriorityQueue;
import gamecore.datastructures.tuples.Pair;
import gamecore.datastructures.tuples.Quadruple;
import gamecore.datastructures.vectors.Vector2d;
import gamecore.datastructures.vectors.Vector2i;
import gamecore.input.InputManager;
import gamecore.input.InputMap;
import maze.collision.CollisionEngine;
import maze.tile.MazeBigTile;
import maze.tile.MazeBigTile.Exit;
import maze.tile.MazeBigTile.TileTypes;

/**
 * Creates a maze exploration game.
 * @author Dawn Nye
 */
public class Maze extends GameEngine
{
	/**
	 * Constructor of the maze
	 * @param width the width of the maze
	 * @param height the height of the maze
	 */
	public Maze(int width, int height)
	{
		super("CSC 207 Maze",null,16 * 3 * width + 16,16 * 3 * height + 39);
		
		Width = width;
		Height = height;
	}
	
	@Override
	/**
	 * Performs any initialization logic before game component initialization logic is executed.
	 */
	protected void Initialize() 
	{
		// Initialize input data
		Input = new InputManager();
		InputMap Bindings = InputMap.Map();
		
		// Add the input manager to the game and make it as a service
		AddComponent(Input);
		AddService(Input);
		
		// Initialize some key bindings
		Bindings.AddKeyBinding("Exit",KeyEvent.VK_ESCAPE);
		
		Bindings.AddKeyBinding("m_A",KeyEvent.VK_SPACE);
		Bindings.AddKeyBinding("a_A",KeyEvent.VK_E);
		Bindings.AddORBinding("A","m_A","a_A");
		
		Bindings.AddKeyBinding("m_Left",KeyEvent.VK_LEFT);
		Bindings.AddKeyBinding("a_Left",KeyEvent.VK_A);
		Bindings.AddORBinding("Left","m_Left","a_Left");
		
		Bindings.AddKeyBinding("m_Right",KeyEvent.VK_RIGHT);
		Bindings.AddKeyBinding("a_Right",KeyEvent.VK_D);
		Bindings.AddORBinding("Right","m_Right","a_Right");
		
		Bindings.AddKeyBinding("m_Up",KeyEvent.VK_UP);
		Bindings.AddKeyBinding("a_Up",KeyEvent.VK_W);
		Bindings.AddORBinding("Up","m_Up","a_Up");
		
		Bindings.AddKeyBinding("m_Down",KeyEvent.VK_DOWN);
		Bindings.AddKeyBinding("a_Down",KeyEvent.VK_S);
		Bindings.AddORBinding("Down","m_Down","a_Down");
		
		// Initialize some input tracking
		Input.AddInput("Exit",() -> Bindings.GetBinding("Exit").DigitalEvaluation.Evaluate());
		Input.AddInput("Left",() -> Bindings.GetBinding("Left").DigitalEvaluation.Evaluate());
		Input.AddInput("Right",() -> Bindings.GetBinding("Right").DigitalEvaluation.Evaluate());
		Input.AddInput("Up",() -> Bindings.GetBinding("Up").DigitalEvaluation.Evaluate());
		Input.AddInput("Down",() -> Bindings.GetBinding("Down").DigitalEvaluation.Evaluate());
		Input.AddInput("A",() -> Bindings.GetBinding("A").DigitalEvaluation.Evaluate(),true);
		
		// Initialize the collision engine
		CollisionResolver = new CollisionEngine();
		AddService(CollisionResolver);
		
		// Generate a new maze
		try {
			GenerateNewMaze();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return;
	}
	
	/**
	 * Generates a new maze.
	 * @throws IOException 
	 */
	public void GenerateNewMaze() throws IOException
	{
		// Clear the components (but not the important ones)
		RemoveComponent(Input,false);
		RemoveComponent(CollisionResolver,false);
		
		ClearComponents();
		CollisionResolver.Clear();
		
		AddComponent(Input);
		
		// Add the player first so that it's on top of everything else
		// We translate it to its start position later
		AddComponent(player = new Player());
		PutService(Player.class,player);
		
		//Linking all values together
		FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>> Map= new FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>>(this.Height,this.Width);
		
		//Setting the tuple for each cell
		//0 means no weight, 1 means that this linkage is assigned with weight, 2 means that this linkage is linked
		for(Vector2i v: Map.IndexSet()){
		 Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(0,0,0,0), v);
		}
		
		//having a new start point
		Random rand= new Random();
		Start= new Vector2i(rand.nextInt(this.Height-1),rand.nextInt(this.Width-1));
		this.player.Translate(new Vector2d(16*(1+3*Start.X),16*(1+3*Start.Y)));

		// Generate the map
		PriorityQueue<Pair<Integer,Pair<Vector2i,Vector2i>>> Weight= new PriorityQueue<Pair<Integer,Pair<Vector2i,Vector2i>>>((p1,p2)->{
			return ((Integer)p1.Item1).intValue()-((Integer)p2.Item1).intValue();
		});
		
		//Adding Elements
		Addlink(Map,Weight,Start);
		
		//Building the Map (for real)
		while(!Weight.IsEmpty()) {
			Pair <Integer,Pair<Vector2i,Vector2i>> p= Weight.Dequeue();//Getting the next linkage
			
			if(Islinked(Map,p)){ //check whether the potential vertex is in the tree
				 continue;
			}
			
			Link(Map,p); //form linkage
			
			Addlink(Map,Weight,p.Item2.Item2); //Adding more potential linkage with weight in Weight
			
			this.End=p.Item2.Item2; //Updating the end
			
		}
		
		if((this.End.X!=0&&this.End.X!=(this.Width-1))||(this.End.Y!=0&&this.End.Y!=(this.Height-1))) {//if the end is not at the appropriate position, we reset the exit
			Defaultexit(Map);
			
		}
		
		DeadEnd(Map); //Determining all the dead ends
		
		SettingTeleport(); //Determining the teleport
		SettingDestination(); //Determining the destination of teleport
		SettingDisplacement();
		
		// Make sure everything gets added to the collision engine fully
		for(int i=0; i<this.Height; i++) {
			for(int j=0; j<this.Width; j++) {
				Visualize(i,j,Map); //visualize all the image
			}
		}
		
		
		CollisionResolver.Flush();
		
		return;
	}
	
	/**
	 * Checking for whether the potential vertex being connected or not
	 * @param Map FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>>  A gird recording the exits
	 * @param p Pair<Integer,Pair<Vector2i,Vector2i>> A pair with item 1 as the weight of the link, item2 as a link from the first item to the second item
	 * @return boolean true->the vertex is being connected false->the vertex is not being connected
	 */
	protected boolean Islinked(FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>> Map, Pair<Integer,Pair<Vector2i,Vector2i>> p){
		Vector2i current= p.Item2.Item2;

		Integer[] existence = new Integer[4];//the tuple of the previous 
		existence[0]=Map.Get(current.X,current.Y).Item1;
		existence[1]=Map.Get(current.X,current.Y).Item2;
		existence[2]=Map.Get(current.X,current.Y).Item3;
		existence[3]=Map.Get(current.X,current.Y).Item4;
		
		for(int i=0; i<4; i++){	
			if(existence[i]==2) {
				return true;
			}
		}
		return false;
	}
	
	/**
	 * Forming a link between two vertex (as the path shown on the graph
	 * @param Map FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>>  A gird recording the exits
	 * @param p Pair<Integer,Pair<Vector2i,Vector2i>> A pair with item 1 as the weight of the link, item2 as a link from the first item to the second item
	 */
	protected void Link(FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>> Map, Pair<Integer,Pair<Vector2i,Vector2i>> p){
		Vector2i previous= p.Item2.Item1;
		Vector2i current= p.Item2.Item2;
		Vector2i difference= current.Subtract(previous); //using to determin with tuple among four need to change
		Vector2i[] directions = new Vector2i[4];//searching directions
		directions[0]=new Vector2i(0,1);//down
		directions[1]=new Vector2i(1,0);//right
		directions[2]=new Vector2i(0,-1);//up
		directions[3]=new Vector2i(-1,0);//left
		for(int i=0; i<4; i++){	
			if(difference.equals(directions[i])){
				switch(i){//letting the other node of the linkage also get the notice that there is a linkage formed between them
				case 0: 
					//previous down=current up
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(previous).Item1+1,Map.Get(previous).Item2,Map.Get(previous).Item3,Map.Get(previous).Item4), previous);
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(current).Item1,Map.Get(current).Item2,Map.Get(current).Item3+1,Map.Get(current).Item4), current);
					break;
				case 1:
					//previous right= current left
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(previous).Item1,Map.Get(previous).Item2+1,Map.Get(previous).Item3,Map.Get(previous).Item4), previous);
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(current).Item1,Map.Get(current).Item2,Map.Get(current).Item3,Map.Get(current).Item4+1), current);
					break;
				case 2:
					//previous up=current down
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(previous).Item1,Map.Get(previous).Item2,Map.Get(previous).Item3+1,Map.Get(previous).Item4), previous);
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(current).Item1+1,Map.Get(current).Item2,Map.Get(current).Item3,Map.Get(current).Item4), current);
					break;
				case 3:
					//previous left=current right
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(previous).Item1,Map.Get(previous).Item2,Map.Get(previous).Item3,Map.Get(previous).Item4+1), previous);
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(current).Item1,Map.Get(current).Item2+1,Map.Get(current).Item3,Map.Get(current).Item4), current);
					
					break;
				}
				return;
			}
		}

	}
	
	
	/**
	 * Adding 4 potential linkage of the given vertex to the priority queue
	 * This function also set the weight of each potential linkage
	 * @param Map FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>>  A gird recording the exits
	 * @param Weight PriorityQueue<Pair<Integer,Pair<Vector2i,Vector2i>>> A priority queue record the weight of each potential linkage
	 * @param Current Vector2i the position the newly added vertex to the graph
	 */
	protected void Addlink(FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>> Map,PriorityQueue<Pair<Integer,Pair<Vector2i,Vector2i>>> Weight,Vector2i Current) {
		Vector2i[] directions = new Vector2i[4];
		directions[0]=new Vector2i(0,1); //down
		directions[1]=new Vector2i(1,0);//right
		directions[2]=new Vector2i(0,-1);//up
		directions[3]=new Vector2i(-1,0);//left
		//Generator for random value
		Random rand=new Random();

		Integer[] existence = new Integer[4]; //recording four potential linkage of the vertex from four directions
		existence[0]=Map.Get(Current.X,Current.Y).Item1;
		existence[1]=Map.Get(Current.X,Current.Y).Item2;
		existence[2]=Map.Get(Current.X,Current.Y).Item3;
		existence[3]=Map.Get(Current.X,Current.Y).Item4;
		
		for (int i=0; i<4; i++) {//assigning weight for each linkage 
			
			Vector2i dir= directions[i];
			Vector2i temp= Current;

			temp=temp.Add(dir);
			
			if(temp.X<0||temp.X==this.Width||temp.Y<0||temp.Y==Height) {//out of bound check
				existence[i]=1;
			}
			else if(existence[i]==0){ //0 means no weight, 1 means that this linkage is assigned with weight, 2 means that this linkage is linked
				existence[i]=1;
				Pair<Vector2i,Vector2i> pos = new Pair<Vector2i, Vector2i>(Current,temp);
				Pair <Integer,Pair<Vector2i,Vector2i>> p = new Pair<Integer, Pair<Vector2i, Vector2i>>(rand.nextInt(this.Height*this.Width+100), pos);//assigning a value to this link
				Weight.Add(p); //Adding this linkage to the priority queue	
				//letting the other node of the linkage also get the notice that there is a potential linkage formed between them
				switch(i){
				case 0: 
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(temp).Item1,Map.Get(temp).Item2,Map.Get(temp).Item3+1,Map.Get(temp).Item4), temp);
					
					break;
				case 1:
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(temp).Item1,Map.Get(temp).Item2,Map.Get(temp).Item3,Map.Get(temp).Item4+1), temp);
					
					break;
				case 2:
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(temp).Item1+1,Map.Get(temp).Item2,Map.Get(temp).Item3,Map.Get(temp).Item4), temp);
					
					break;
				case 3:
					Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(Map.Get(temp).Item1,Map.Get(temp).Item2+1,Map.Get(temp).Item3,Map.Get(temp).Item4), temp);
					
					break;
				}	
			}
			//update that there is value given to these potential linkage
			Map.Set(new Quadruple<Integer,Integer,Integer,Integer>(existence[0],existence[1],existence[2],existence[3]), Current);} 
	}
	
	/**
	 * If the end is not at the appropriate position(edge of the maze), 
	 * we reset the exit by letting it be on the edge
	 * @param Map FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>>  A gird recording the exits
	 */
	public void Defaultexit(FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>> Map) {
		Random rand= new Random();

		//Using different edges->to create more variability of exits
		
		//bottom edge
			if (Map.Get(new Vector2i(rand.nextInt(this.Width-1),this.Height-1)).Item3==2) {
				this.End= new Vector2i(rand.nextInt(this.Width-1),this.Height-1); //let the exit be at bottom edge
				return;
			}
		
			//top edge
			if (Map.Get(new Vector2i(rand.nextInt(this.Width-1),0)).Item1==2) {
				this.End= new Vector2i(rand.nextInt(this.Width-1),0);// the exit be at top edge
				return;
			}
		
		
		//left edge
			if (Map.Get(new Vector2i(0,rand.nextInt(this.Height-1))).Item1==2) {
				this.End= new Vector2i(0,rand.nextInt(this.Height-1));// the exit be at top edge
				return;
			}
		
		//right edge
		for(int i=0; i< this.Width;i++) {
			if (Map.Get(new Vector2i(this.Width-1,rand.nextInt(this.Height-1))).Item1==2) {
				this.End= new Vector2i(this.Width-1,rand.nextInt(this.Height-1));// the exit be at top edge
				return;
			}
		}

	}

	/**
	 * Find all the dead end in the Map
	 * @param Map FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>>  A gird recording the exits
	 * @return
	 */
	public void DeadEnd(FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>> Map) {

		Deadends= new ArrayList<Vector2i>(); //the place to store the data

		for (int i=0; i<this.Height; i++) {
			for(int j=0; j<this.Width; j++) {
				//if it is a dead end, its sum of the item is 5 (3 walls + 1 exit)
				int sum=Map.Get(new Vector2i(j,i)).Item1+
						Map.Get(new Vector2i(j,i)).Item2+
						Map.Get(new Vector2i(j,i)).Item3+
						Map.Get(new Vector2i(j,i)).Item4;
				
				if(sum==5) {
					Deadends.Add(new Vector2i(j,i));
				}
				
			}
		}
		
		//Avoiding end and start
		Deadends.Remove(this.End);
		Deadends.Remove(this.Start);
	}
	
	
	/**
	 * Generate teleport randomly with the chance as 0.2
	 */
	public void SettingTeleport() {
		Teleporters= new ArrayList<Vector2i>(); //the place to store the teleport position

		Random rand= new Random();
		
		for(Vector2i v : Deadends) {
			int n = rand.nextInt(10);
			if(Teleporters.size()< MAX_TELEPORTERS) {//limit of the number of teleport
				if(n==5||n==3) {
					Teleporters.Add(v);
				}
			}
		}
	}

	/**
	 * Generate destination randomly according to the number of teleport
	 */
	public void SettingDestination() {
		Random rand= new Random();
		Destinations= new ArrayList<Vector2i>(); //the place to store the destination position
		
		while(Destinations.size()<Teleporters.size()) {
			int n = rand.nextInt(Deadends.size());
			Vector2i temp=Deadends.get(n);
			if(Teleporters.Contains(temp)) {//Avoid duplication
				continue;
			}
			if(Destinations.Contains(temp)) {//Avoid duplication
				continue;
			}
			else {
				Destinations.Add(temp);
			}
			
		}
	}

	/**
	 * Calculate the destination of between each pair of destination and teleport
	 */
	public void SettingDisplacement() {
		Displacements= new ArrayList<Vector2d>();
		int num= Teleporters.size();
		for(int i=0; i<num; i++) {
			Vector2i t= Teleporters.get(i);
			Vector2i d= Destinations.get(i);
			Vector2i dis=d.Subtract(t); //calculate the difference between destination and teleport
			Vector2d distance=new Vector2d(dis.X*16.0*3,dis.Y*16.0*3);//calculate the place they actually need to transport
			Displacements.Add(distance);
		}
	}
	
	/**
	 * Assigning appropriate type of exit according to the position of the end of the maze
	 * @param pos Vector2i the position of the end of the maze
	 * @return Exit a element in a enum
	 */
	protected Exit AssignExit(Vector2i pos) {
		if(pos.X==(this.Width-1) && pos.Y==(this.Height-1) ) {//at bottom right corner
			return Exit.DOWN;
		}
		if(pos.X==0 && pos.Y==0 ) {//at top left
			return Exit.LEFT;
		}
		if(pos.X==(this.Width-1) && pos.Y==0 ) {//at top right corner
			return Exit.RIGHT;
		}
		if(pos.X==0 && pos.Y==(this.Height-1) ) {//at bottom left corner
			return Exit.LEFT;
		}
		
		if(pos.X==0) {//on the left
			return Exit.LEFT;
		}
		if(pos.Y==0) {//on the top
			return Exit.UP;
		}
		if(pos.X==(this.Width-1)) {//on the right
			return Exit.RIGHT;
		}
		if(pos.Y==(this.Height-1)) {//on the bottom
			return Exit.DOWN;
		}
		
		return Exit.DOWN;
	}
	
	/**
	 * Visualizing all the elements of the maze except player 
	 * @param i int Height of the maze
	 * @param j int Width of the maze
	 * @param Map FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>> A gird to record all the exits
	 * @throws IOException
	 */
	protected void Visualize(int i, int j,FixedSizeGrid<Quadruple<Integer,Integer,Integer,Integer>> Map) throws IOException {
		
		this.View= new  MazeBigTile[this.Height][this.Width];
		
		Vector2i pos= new Vector2i(j,i);
		
		EnumSet<MazeBigTile.Exit> exits= EnumSet.noneOf(MazeBigTile.Exit.class);
		
		//storing the exits into an iterator
		if(Map.Get(pos).Item1==2) {
			exits.add(MazeBigTile.Exit.DOWN);
		}
		if(Map.Get(pos).Item2==2) {
			exits.add(MazeBigTile.Exit.RIGHT);
		}
		if(Map.Get(pos).Item3==2) {
			exits.add(MazeBigTile.Exit.UP);
		}
		if(Map.Get(pos).Item4==2) {
			exits.add(MazeBigTile.Exit.LEFT);
		}
		
		
		
		if(pos.equals(this.End)) {//end 
			Exit true_exit= AssignExit(pos); //assign appropriate type of exit to the end
			View[i][j]=new MazeBigTile(TileTypes.PLAIN,exits,true_exit,pos,this.Width, this.Height); 
		}
		else if(pos.equals(this.Start)) {//start
			View[i][j]=new MazeBigTile(exits,pos); 
		}
		else if(Teleporters.Contains(pos)) {//teleport
			int index=0;
			for(int n=0; n<Teleporters.size(); n++) {
				Vector2i temp=Teleporters.get(n);
				if(temp.equals(pos)) {
					index=n;
				}
			}
			View[i][j]=new MazeBigTile(TileTypes.TELEPORTER,exits,Displacements.get(index),pos);
			
		}
		else if(Destinations.Contains(pos)) {//destination
			View[i][j]=new MazeBigTile(TileTypes.TELEPORT_DESTINATION,exits,pos);
		}
		else {//normal part
			View[i][j]=new MazeBigTile(TileTypes.PLAIN,exits, pos);
		}
		
		View[i][j].OnAdd(); //Adding it on the screen
	}
	
	@Override 
	/**
	 * Performs any initialization logic after game component initialization logic is executed.
	 */
	protected void LateInitialize()
	{
		if(!CollisionResolver.Initialized())
			CollisionResolver.Initialize();
		
		return;
	}
	
	@Override
	/**
	 * Performs any update logic before game components' update logic is executed.
	 */
	protected void Update(long delta)
	{		
		if(this.player.GetBoundary().Center().X<0 ||this.player.GetBoundary().Center().Y<0||this.player.GetBoundary().Center().X>16 * 3 * this.Width+1 ||this.player.GetBoundary().Center().Y>16 * 3 *this.Height+1) {
			this.player.OnRemove();
			this.Dispose();
			try {
				GenerateNewMaze();
			} 
			catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}


		return;}

	@Override 
	/**
	 * Performs any update logic after game components' update logic is executed.
	 */
	protected void LateUpdate(long delta)
	{
		if(Input.GracelessInputSatisfied("Exit"))
			Quit();
		
		// We resolve collisions last so that hopefully Java's swing library will paint after we do that and we won't see ugly in between states
		CollisionResolver.Update(delta);
		
		return;
	}
	
	@Override 
	/**
	 * Performs any disposal logic before game components' disposal logic is executed.
	 */
	protected void Dispose()
	{
		for (int i=0; i<this.Width; i++) {
			for(int j=0; j<this.Height;j++) {
				if(this.View[i][j]!=null)
				this.View[i][j].OnRemove();
			}
		}
		
		
		return;}
	
	@Override
	/**
	 * Performs any disposal logic after game components' disposal logic is executed.
	 */
	protected void LateDispose()
	{
		if(!CollisionResolver.Disposed())
			CollisionResolver.Dispose();
		
		return;
	}
	
	
	/**
	 * The input manager for the game.
	 * This is registered as a service.
	 */
	protected InputManager Input;
	
	/**
	 * The player.
	 */
	protected Player player;
	
	/**
	 * The collision resolution engine.
	 */
	protected CollisionEngine CollisionResolver;
	
	/**
	 * The width of the board.
	 */
	protected int Width;
	
	/**
	 * The height of the board.
	 */
	protected int Height;
	/**
	 * The gird for the whole maze visualization
	 */
	protected MazeBigTile View[][];
	/**
	 * The position of the exit of the maze
	 */
	protected Vector2i End;
	
	/**
	 * The position of the start of the maze
	 */
	protected Vector2i Start;
	/**
	 * The arraylist store all the deadends
	 */
	protected ArrayList<Vector2i> Deadends= new ArrayList<Vector2i>();
	/**
	 * The arraylist store all the teleporters
	 */
	protected ArrayList<Vector2i> Teleporters;
	/**
	 * The arraylist store all the destinations
	 */
	protected ArrayList<Vector2i> Destinations;
	/**
	 * The arraylist store all the displacements
	 */
	protected ArrayList<Vector2d> Displacements;
	
	
	
	
	
	
	/**
	 * The maximum number of teleporters allowed.
	 * This value is arbitrary and could be ignored.
	 */
	protected final static int MAX_TELEPORTERS = 3;
}
