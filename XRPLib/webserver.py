from phew import server, template, logging, access_point, dns
from phew.template import render_template
from phew.server import redirect
import gc
import network
import time

class Webserver:

    @classmethod
    def get_default_webserver(cls):
        """
        Get the default webserver instance. This is a singleton, so only one instance of the webserver will ever exist.
        """
        return webserver

    def __init__(self):
        """
        Host a webserver for the XRP v2 Robot; Register your own callbacks and log your own data to the webserver using the methods below.
        """

        gc.threshold(50000) # garbage collection
        self.DOMAIN = "remote.xrp"
        self.logged_data = {}
        self.buttons = {"forwardButton":    lambda: logging.debug("Button not initialized"),
                        "backButton":   lambda: logging.debug("Button not initialized"),
                        "leftButton":       lambda: logging.debug("Button not initialized"),
                        "rightButton":      lambda: logging.debug("Button not initialized"),
                        "stopButton":       lambda: logging.debug("Button not initialized")}
        self.FUNCTION_PREFIX = "startfunction"
        self.FUNCTION_SUFFIX = "endfunction"
        self.display_arrows = False

    def start_server(self, robot_number:int):
        """
        Start the webserver

        :param robot_number: The number of the robot, used to generate the access point name
        :type robot_number: int
        """
        self.access_point = access_point(f"XRP_{robot_number}")
        self.ip = network.WLAN(network.AP_IF).ifconfig()[0]
        logging.info(f"Starting DNS Server at {self.ip}")
        dns.run_catchall(self.ip)
        server.run()
        logging.info("Webserver Started")

    def _index_page(self, request):
        # Render index page and respond to form requests
        if request.method == 'GET':
            return self._generateHTML()
        if request.method == 'POST':
            text = list(request.form.keys())[0]
            self._handleUserFunctionRequest(text)
            return self._generateHTML()


    def _wrong_host_redirect(self, request):
        # Catch all sends here. No special behavior really needed, just give them the control page 
        return self._generateHTML()

    def _hotspot(self, request):
        # Redirect to Index Page
        return self._generateHTML()

    def _catch_all(self, request):
        # Catch all requests and redirect if necessary
        if request.headers.get("host") != self.DOMAIN:
            return redirect("http://"+self.DOMAIN+"/wrong-host-redirect")
        return self._index_page(request=request)
        
    def log_data(self, label:str, data):
        """
        Register a custom label to be displayed on the webserver

        :param label: The label as it will be displayed, must be unique
        :type label: str
        :param data: The data to be displayed
        :type data: Any (converted to string)
        """
        self.logged_data[label] = data

    def add_button(self, button_name:str, function):
        """
        Register a custom button to be displayed on the webserver

        :param button_name: The label for the button as it will be displayed, must be unique
        :type button_name: str
        :param function: The function to be called when the button is pressed
        :type function: function
        """
        self.buttons[button_name] = function

    def registerForwardButton(self, function):
        """
        Assign a function to the forward button

        :param function: The function to be called when the button is pressed
        :type function: function
        """
        self.display_arrows = True
        self.buttons["forwardButton"] = function

    def registerBackwardButton(self, function):
        """
        Assign a function to the backward button

        :param function: The function to be called when the button is pressed
        :type function: function
        """
        self.display_arrows = True
        self.buttons["backButton"] = function
    
    def registerLeftButton(self, function):
        """
        Assign a function to the left button

        :param function: The function to be called when the button is pressed
        :type function: function
        """
        self.display_arrows = True
        self.buttons["leftButton"] = function

    def registerRightButton(self, function):
        """
        Assign a function to the right button

        :param function: The function to be called when the button is pressed
        :type function: function
        """
        self.display_arrows = True
        self.buttons["rightButton"] = function
    
    def registerStopButton(self, function):
        """
        Assign a function to the stop 
        
        :param function: The function to be called when the button is pressed
        :type function: function
        """
        self.display_arrows = True
        self.buttons["stopButton"] = function

    def _handleUserFunctionRequest(self, text) -> bool:
        print(f"Running {text}")
        try:
            user_function = self.buttons[text]
            if user_function is None:
                print("User function "+text+" not found")
                return False
            user_function()
            return True
        except:
            print("User function "+text+" caused an exception")
            return False

    def _generateHTML(self):

        string = _HTML1
        
        if self.display_arrows:
            string += _HTML_ARROWS

        string += f'<h3>Custom Function Bindings:</h3>'
        # add each button's href to html
        for button in self.buttons.keys():
            if(["forwardButton","backButton","leftButton","rightButton","stopButton"].count(button) > 0):
                # Slightly cursed solution to not display the arrow buttons as text buttons
                continue
            string += f'<p><form action="{button}" method="post"><input type="submit" class="user-button" name={button} value="{button}" /></form></p>'
            string += "\n"

        string += f'<h3>Logged Data:</h3>'
        # add logged data to the html
        for data_label in self.logged_data.keys():
            string += f'<p>{data_label}: {str(self.logged_data[data_label])}</p>'
            string += "\n"

        string += _HTML2

        return string

""" Use decorators to bind the wifi methods to the requests """
webserver = Webserver()

@server.route("/", methods=['GET','POST'])
def index(request):
    return webserver._index_page(request)

@server.route("/wrong-host-redirect", methods=['GET'])
def wrong_host_redirect(request):
    return webserver._wrong_host_redirect(request)

@server.route("/hotspot-detect.html", methods=["GET"])
def hotspot(request):
    return webserver._hotspot(request)

@server.catchall()
def catch_all(request):
    return webserver._catch_all(request)

_HTML1 = """
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta http-equiv="refresh" content="1">
            
            <style>
                a { text-decoration: none; }

                html {
                    font-family: Arial;
                    display: inline-block;
                    margin: 0px auto;
                    text-align: center;
                }

                .arrow-button {
                    font-size: 30px;
                }

                .user-button {
                    font-size: 20px;
                }
            </style>
            
        </head>

        <body>
            <h2>XRP control page</h2>

            <p>
"""

_HTML_ARROWS = """
        <form action="forwardButton" method="post"><input type="submit" class="arrow-button" name="forwardButton" value=&#8593; /></form>
        <div style="display: flex; justify-content: center;">
        <form action="leftButton" method="post"><input type="submit" class="arrow-button" name="leftButton" value=&#8592; /></form>
        &nbsp;&nbsp;
        <form action="stopButton" method="post"><input type="submit" class="arrow-button" name="stopButton" value=&#9744; /></form>
        &nbsp;&nbsp;
        <form action="rightButton" method="post"><input type="submit" class="arrow-button" name="rightButton" value=&#8594; /></form>
        </div>
        <form action="backButton" method="post"><input type="submit" class="arrow-button" name="backButton" value=&#8595; /></form>
"""

_HTML2 = """
            </p>

        </body>

        </html>
"""