import pygame
from typing import List, Tuple, Any, Union, Dict, Optional
import cv2

# Importing relevant modules that encapsulate functionality for the game states, buttons, dances, poses, video handling, and settings.
from .state_module import Game_State
from .button_module import Text_Button, Image_Button
from .dance_module import Dance
from .pose_module import Pose_Landmarker_Model, Pose, compare_poses
from .video_module import Video_Capture_Handler
from .settings_module import Settings


class Main_Menu(Game_State):
    """
    Represents the main menu of the game.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the main menu with title text, fonts, and buttons.
        """
        super().__init__()
        self.settings = settings

        # Set up fonts and title text
        self.titel_font = pygame.Font(self.settings.path.BLOCKY_FONT_PATH, 100)
        self.button_font = pygame.Font(self.settings.path.BLOCKY_FONT_PATH, 60)
        self.main_menu_text = self.titel_font.render("Dance Match", True, color=(207, 186, 240))
        self.main_menu_text_rect = self.main_menu_text.get_rect(center=(self.settings.display.WIDTH / 2, 100))

        # Create and position buttons
        self.buttons: List[Text_Button] = []

        self.play_button = Text_Button(
            "Play",
            (self.settings.display.WIDTH / 2, self.settings.display.HEIGHT / 2),
            normal_color=self.settings.button.NORMAL_COLOR,
            hover_color=self.settings.button.HOVER_COLOR,
            pressed_color=self.settings.button.PRESSED_COLOR,
            font=self.button_font,
            callback=lambda: self._button_callback(self.settings.state.STATE_DANCE_SELECTION_KEY)
        )
        self.play_button.rect.center = ((self.settings.display.WIDTH / 2, self.settings.display.HEIGHT / 2))
        self.buttons.append(self.play_button)

        self.quit_button = Text_Button(
            "Quit",
            (self.settings.display.WIDTH / 2, self.settings.display.HEIGHT / 2 + 100),
            normal_color=self.settings.button.NORMAL_COLOR,
            hover_color=self.settings.button.HOVER_COLOR,
            pressed_color=self.settings.button.PRESSED_COLOR,
            font=self.button_font,
            callback=lambda: self._button_callback(self.settings.state.QUIT_KEY)
        )
        self.quit_button.rect.center = ((self.settings.display.WIDTH / 2, self.settings.display.HEIGHT / 2 + 100))
        self.buttons.append(self.quit_button)

        self.button_callback_queue = []  # Queue for button callbacks

    def _button_callback(self, data: Any) -> None:
        """
        Handle button click callbacks by adding the result to the queue.
        """
        self.button_callback_queue.append(data)

    def handle_events(self, event: pygame.event.Event) -> None:
        """
        Handle events for all buttons in the menu.
        """
        for button in self.buttons:
            button.handle_events(event)

    def render(self, render_surface: pygame.Surface) -> None:
        """
        Render the main menu UI, including the title text and buttons.
        """
        render_surface.fill((255, 255, 255))  # Fill background with white
        render_surface.blit(self.main_menu_text, self.main_menu_text_rect)  # Render title text

        for button in self.buttons:
            button.render(render_surface)

    def update(self, dt: float) -> None:
        """
        Update button states and check for callbacks.
        """
        for button in self.buttons:
            button.update()

        if self.button_callback_queue:
            return self.button_callback_queue.pop(0)

class Dance_Selection(Game_State):
    def __init__(self, settings: Settings, dances: Dict[int, Dance]) -> None:
        """
        Initializes the Dance_Selection screen.
        """
        super().__init__()
        self.settings = settings
        self.dances = dances
        
        # Initialize UI components
        self.top_banner_surface = pygame.Surface((self.settings.display.WIDTH, 150))
        self.top_banner_surface.fill((220, 220, 220))
        self.top_banner_rect = self.top_banner_surface.get_rect(topleft=(0, 0))
        
        self.bottom_banner_surface = pygame.Surface((self.settings.display.WIDTH, 100))
        self.bottom_banner_surface.fill((220, 220, 220))
        self.bottom_banner_rect = self.bottom_banner_surface.get_rect(bottomleft=(0, self.settings.display.HEIGHT))

        self.blocky_font = pygame.Font(self.settings.path.BLOCKY_FONT_PATH, 70)
        self.level_select_text = self.blocky_font.render("Level Select", True, (140, 140, 140))
        self.level_select_text_rect = self.level_select_text.get_rect(center=(self.settings.display.WIDTH / 2, self.top_banner_rect.centery))

        self.buttons = []
        self.dance_buttons = []
        self.button_callback_queue = []
        self.dance_buttons_positions = [
            (self.settings.display.WIDTH / 2 - 200, self.settings.display.HEIGHT / 2 - 100 + 40), 
            (self.settings.display.WIDTH / 2 + 200, self.settings.display.HEIGHT / 2 - 100 + 40), 
            (self.settings.display.WIDTH / 2 - 200, self.settings.display.HEIGHT / 2 + 100 + 60), 
            (self.settings.display.WIDTH / 2 + 200, self.settings.display.HEIGHT / 2 + 100 + 60)
        ]

        self._create_buttons()

    def _button_callback(self, data: Any) -> None:
        """
        Adds the given data to the button callback queue.

        Args:
            data (Any): The data to be added to the callback queue.
        """
        self.button_callback_queue.append(data)
    
    def _create_buttons(self) -> None:
        """
        Creates the buttons for the dance selection screen.
        """
        # Create the back button
        self.back_button_font = pygame.Font(self.settings.path.BLOCKY_FONT_PATH, 30)
        self.back_button = Text_Button(
            text="Back",
            position=(0, 0),
            normal_color=self.settings.button.NORMAL_COLOR,
            hover_color=self.settings.button.HOVER_COLOR,
            pressed_color=self.settings.button.PRESSED_COLOR,
            font=self.back_button_font,
            callback=lambda: self._button_callback(self.settings.state.STATE_MAIN_MENU_KEY)
        )
        self.back_button.rect.midleft = (
            self.bottom_banner_rect.height / 2 + self.bottom_banner_rect.x,
            self.bottom_banner_rect.height / 2 + self.bottom_banner_rect.y
        )
        self.buttons.append(self.back_button)

        # Create buttons for each dance
        for i, dance_id in enumerate(self.dances):
            button = Image_Button(
                image=self.dances[dance_id].thumbnail,
                position=(0, 0),
                hover_tint_color=self.settings.button.IMAGE_HOVER_TINT_COLOR,
                pressed_tint_color=self.settings.button.IMAGE_PRESSED_TINT_COLOR,
                hover_tint_intensity=self.settings.button.IMAGE_HOVER_TINT_INTENSITY,
                pressed_tint_intensity=self.settings.button.IMAGE_PRESSED_TINT_INTENSITY,
                callback=lambda dance_id=dance_id: self._button_callback(f"{self.settings.state.PLAY_DANCE_KEY}{dance_id}")
            )
            button.rect.center = self.dance_buttons_positions[i]
            self.buttons.append(button)
            self.dance_buttons.append(button)

    def handle_events(self, event: pygame.event.Event) -> None:
        """
        Handles events on the dance selection screen.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return self.settings.state.STATE_MAIN_MENU_KEY

        for button in self.buttons:
            button.handle_events(event)
    
    def render(self, render_surface: pygame.Surface) -> None:
        """
        Renders the dance selection screen.

        Args:
            render_surface (pygame.Surface): The surface to render onto.
        """
        render_surface.fill((255, 255, 255))
        render_surface.blit(self.top_banner_surface, self.top_banner_rect)
        render_surface.blit(self.level_select_text, self.level_select_text_rect)

        for button in self.buttons:
            button.render(render_surface)
    
    def update(self, dt: float) -> Optional[str]:
        """
        Updates the dance selection screen.

        Args:
            dt (float): Time elapsed since the last update.

        Returns:
            Optional[str]: Callback result, if available.
        """
        for button in self.buttons:
            button.update()

        if self.button_callback_queue:
            return self.button_callback_queue.pop(0)


class Play_Dance(Game_State):
    """
    Represents the state where the player performs a dance in the game.
    """
    
    def __init__(self, settings: Settings, dance: Dance, webcam: Video_Capture_Handler) -> None:
        """
        Initializes the Play_Dance state.

        Args:
            settings (Settings): Game settings containing configuration details.
            dance (Dance): The current dance routine.
            webcam (Video_Capture_Handler): Webcam handler for capturing video frames.
        """
        self.settings = settings
        self.dance = dance
        self.webcam = webcam

        self.frame_surface = pygame.Surface((0, 0))

        # Countdown-related attributes
        self.countdown_active = True
        self.countdown_length_ms = 4000  # 4 seconds countdown
        self.countdown_start_time_ms = pygame.time.get_ticks()
        self.countdown_time_remaining = self.countdown_length_ms
        self.countdown_text = ""
        self.countdown_font = pygame.Font(self.settings.path.BLOCKY_FONT_PATH, 80)

        # Dance-related attributes
        self.dance_active = False
        self.dance_start_time_ms = 0
        self.dance_dist_font = pygame.Font(self.settings.path.BLOCKY_FONT_PATH, 30)

        # Pose detection model
        self.pose_model = Pose_Landmarker_Model(self.settings.path.LANDMARK_MODEL_PATH)
        self.pose_model.initialize()

        # Pose sequence for the dance
        self.dance_pose_sequence = self.dance.get_pose_sequence()

        # Performance tracking
        self.current_distances = []
        self.batch_averages = []
        self.batch_size = 20
        self.dist = 10
        self.current_batch_average = 2

    def _track_performance(self) -> None:
        """
        Tracks the performance by calculating the average distance for the current batch
        and storing it in the batch averages list.
        """
        if len(self.current_distances) >= self.batch_size:
            batch_average = sum(self.current_distances) / len(self.current_distances)
            self.batch_averages.append(batch_average)
            self.current_distances.clear()
            self.current_batch_average = batch_average

    def get_final_score(self) -> int:
        """
        Calculates the final score based on average batch distances.

        Returns:
            int: The final score (0 to 3) based on performance.
        """
        if not self.batch_averages:
            return 0
        
        average = sum(self.batch_averages) / len(self.batch_averages)

        if average < 0.4: return 3
        if average < 0.9: return 2
        if average < 1.6: return 1
        return 0

    def start_dance(self) -> None:
        """
        Starts the dance routine and resets the video position to the beginning.
        """
        self.dance_active = True
        self.dance.video.set_position_msec(0)
        self.dance_start_time_ms = pygame.time.get_ticks()

    def handle_events(self, event: pygame.event.Event) -> None:
        """
        Handles events during the dance routine.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        pass

    def render_dance(self, render_surface: pygame.Surface) -> None:
        """
        Renders the dance video and current performance metrics.

        Args:
            render_surface (pygame.Surface): The surface to render onto.
        """
        render_surface.blit(self.frame_surface, (0, 0))

        surf = self.dance_dist_font.render(str(round(self.current_batch_average, 2)), True, (255, 0, 0))
        rect = surf.get_rect(midbottom=(self.settings.display.WIDTH / 2, self.settings.display.HEIGHT))
        render_surface.blit(surf, rect)

    def render_countdown(self, render_surface: pygame.Surface) -> None:
        """
        Renders the countdown text.

        Args:
            render_surface (pygame.Surface): The surface to render onto.
        """
        countdown_text_surface = self.countdown_font.render(self.countdown_text, True, (0, 255, 0))
        countdown_text_surface_rect = countdown_text_surface.get_rect(center=(self.settings.display.WIDTH / 2, self.settings.display.HEIGHT / 2))
        render_surface.blit(countdown_text_surface, countdown_text_surface_rect)

    def render(self, render_surface: pygame.Surface) -> None:
        """
        Renders the current game state.

        Args:
            render_surface (pygame.Surface): The surface to render onto.
        """
        render_surface.fill((255, 255, 255))

        if self.countdown_active:
            self.render_countdown(render_surface)
        
        if self.dance_active:
            self.render_dance(render_surface)

    def update_dance(self) -> Optional[bool]:
        """
        Updates the dance routine by synchronizing the video, processing webcam frames,
        and calculating pose distances.

        Returns:
            Optional[bool]: True if the video has ended, else None.
        """
        current_time_ms = pygame.time.get_ticks() - self.dance_start_time_ms
        current_video_timestamp_ms = int(self.dance.video.cap.get(cv2.CAP_PROP_POS_MSEC))
        self.dance.video.set_position_msec(current_time_ms)

        webcam_ret, webcam_frame = self.webcam.read_frame()
        video_ret, video_frame = self.dance.video.read_frame()

        if webcam_ret:
            rgb_frame = cv2.cvtColor(webcam_frame, cv2.COLOR_BGR2RGB)

            self.pose_model.process_frame(rgb_frame, current_time_ms)
            result = self.pose_model.get_latest_result()

            if result is not None:
                web_pose = Pose(result.pose_landmarks, current_time_ms)
                video_pose = self.dance_pose_sequence.get_closest_pose_at(current_video_timestamp_ms)

                dist = compare_poses(web_pose, video_pose)
                if dist is not None:
                    self.dist = dist
                    self.current_distances.append(self.dist)

        if video_ret:
            video_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            video_frame = cv2.flip(video_frame, 1)  # Flip horizontally
            self.frame_surface = pygame.surfarray.make_surface(video_frame.swapaxes(0, 1))

            scale = self.settings.display.WIDTH / self.frame_surface.get_width()
            self.frame_surface = pygame.transform.scale(self.frame_surface, (int(self.frame_surface.get_width() * scale), int(self.frame_surface.get_height() * scale)))
        else:
            return True
        
        self._track_performance()

    def update_countdown(self) -> None:
        """
        Updates the countdown timer and starts the dance when the countdown ends.
        """
        elapsed_time = pygame.time.get_ticks() - self.countdown_start_time_ms
        self.countdown_time_remaining = self.countdown_length_ms - elapsed_time

        if self.countdown_time_remaining < 0:
            self.countdown_active = False
            self.start_dance()
        elif self.countdown_time_remaining < 1000:
            self.countdown_text = "GO"
        else:
            self.countdown_text = str(self.countdown_time_remaining // 1000)

    def update(self, dt: float) -> Optional[str]:
        """
        Updates the game state.

        Args:
            dt (float): Time elapsed since the last update.

        Returns:
            Optional[str]: State transition key if the dance ends, else None.
        """
        if self.countdown_active:
            self.update_countdown()
        
        if self.dance_active:
            ret = self.update_dance()
            if ret:
                self.dance.video.release()
                score = self.get_final_score()
                return f"{self.settings.state.DANCE_SCORE_KEY}{int(score)}"


class Scoreboard(Game_State):
    """
    The Scoreboard class handles the display and interaction of the game's scoreboard.
    It shows the score and provides a button to go back to the dance selection screen.
    """

    def __init__(self, settings: Settings, score: int) -> None:
        """
        Initializes the Scoreboard with the game settings and score.
        
        Args:
            settings (Settings): The configuration settings used for display, buttons, etc.
            score (int): The score to display on the scoreboard.
        """
        self.settings = settings  
        self.score = score  

        self.text = f"You scored {self.score} stars!"
        self.font = pygame.Font(self.settings.path.BLOCKY_FONT_PATH, 70)  
        self.text_surface = self.font.render(self.text, True, (150, 150, 150)) 
        self.text_surface_rect = self.text_surface.get_rect(center=(self.settings.display.WIDTH / 2, 
                                                                   self.settings.display.HEIGHT / 2)) 

        self.buttons = []
        self._create_buttons()

    
        self.button_callback_queue = []
    
    def _button_callback(self, data: Any) -> None:
        """
        Appends the callback data to the button callback queue.
        
        Args:
            data (Any): The data associated with the button press (e.g., the next game state).
        """
        self.button_callback_queue.append(data)

    def _create_buttons(self) -> None:
        """
        Creates buttons for the scoreboard. Currently only a 'Back' button is created.
        The 'Back' button allows the player to return to the dance selection screen.
        """
        self.back_button_font = pygame.Font(self.settings.path.BLOCKY_FONT_PATH, 30) 
        self.back_button = Text_Button(
            text="Back",  
            position=(0, 0),  
            normal_color=self.settings.button.NORMAL_COLOR,  
            hover_color=self.settings.button.HOVER_COLOR,
            pressed_color=self.settings.button.PRESSED_COLOR,
            font=self.back_button_font,  
            callback=lambda: self._button_callback(self.settings.state.STATE_DANCE_SELECTION_KEY) 
        )

        self.back_button.rect.bottomleft = (20, self.settings.display.HEIGHT - 20)
        self.buttons.append(self.back_button) 
    
    def handle_events(self, event: pygame.Event) -> None:
        """
        Handles events for all buttons in the scoreboard.
        
        Args:
            event (pygame.Event): The pygame event to handle (e.g., button clicks).
        """
        for button in self.buttons:
            button.handle_events(event) 

    def render(self, render_surface: pygame.Surface) -> None:
        """
        Renders the scoreboard to the given surface.
        
        Args:
            render_surface (pygame.Surface): The surface to render the scoreboard on.
        """
        render_surface.fill((255, 255, 255))  

        render_surface.blit(self.text_surface, self.text_surface_rect)
        
        for button in self.buttons:
            button.render(render_surface)

    def update(self, dt) -> None:
        """
        Updates the state of the buttons and checks for any callbacks.
        
        Args:
            dt (float): The time delta between frames, passed to buttons for updates.
        """
        for button in self.buttons:
            button.update()  
        
        # Check if any button callbacks were triggered and return the first one in the queue
        if self.button_callback_queue:
            return self.button_callback_queue.pop(0)
