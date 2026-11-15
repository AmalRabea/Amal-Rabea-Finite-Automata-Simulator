import tkinter as tk
from tkinter import ttk, messagebox
import math


class AutomataSimulator:

    def __init__(self, root):
        self.root = root
        self.root.title("Finite Automata Simulator")
        self.root.geometry("1360x760")
        self.root.minsize(1100, 650)
        self.root.configure(bg="#f2f4f8")

        self.mode = tk.StringVar(value="DFA")

        self.states = []
        self.alphabet = []
        self.initial = ""
        self.finals = set()
        self.transitions = {}

        self.word = ""
        self.position = 0
        self.current_states = set()
        self.visited_states = set()
        self.active_edges = set()
        self.path = []
        self.simulation_started = False
        self.simulation_finished = False

        self.create_interface()
        self.load_preset("DFA")

    # ==================================================
    # COMPACT INTERFACE
    # ==================================================

    def create_interface(self):

        header = tk.Frame(self.root, bg="#f2f4f8")
        header.pack(fill="x", pady=(5, 3))

        tk.Label(
            header,
            text="FINITE AUTOMATA SIMULATOR",
            font=("Arial", 19, "bold"),
            bg="#f2f4f8",
            fg="#243b53"
        ).pack()

        tk.Label(
            header,
            text="DFA and NFA Design, Simulation, and Visualization",
            font=("Arial", 9),
            bg="#f2f4f8",
            fg="#52677d"
        ).pack(pady=(1, 3))

        preset_frame = tk.Frame(self.root, bg="#f2f4f8")
        preset_frame.pack(pady=(0, 5))

        tk.Label(
            preset_frame,
            text="Automaton Type:",
            font=("Arial", 10, "bold"),
            bg="#f2f4f8"
        ).pack(side="left", padx=7)

        ttk.Radiobutton(
            preset_frame,
            text="DFA",
            variable=self.mode,
            value="DFA",
            command=lambda: self.load_preset("DFA")
        ).pack(side="left", padx=8)

        ttk.Radiobutton(
            preset_frame,
            text="NFA",
            variable=self.mode,
            value="NFA",
            command=lambda: self.load_preset("NFA")
        ).pack(side="left", padx=8)

        main_frame = tk.Frame(self.root, bg="#f2f4f8")
        main_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(3, 9)
        )

        main_frame.grid_columnconfigure(0, weight=5)
        main_frame.grid_columnconfigure(1, weight=6)
        main_frame.grid_rowconfigure(0, weight=1)

        left_frame = tk.Frame(main_frame, bg="#f2f4f8")
        left_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7)
        )

        right_frame = tk.Frame(main_frame, bg="#f2f4f8")
        right_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(7, 0)
        )

        self.create_configuration(left_frame)
        self.create_simulation(left_frame)
        self.create_diagram(right_frame)

    # ==================================================
    # CONFIGURATION
    # ==================================================

    def create_configuration(self, parent):

        config = tk.LabelFrame(
            parent,
            text="Automaton Configuration",
            font=("Arial", 10, "bold"),
            bg="#f2f4f8",
            padx=8,
            pady=5
        )
        config.pack(fill="x", pady=(0, 5))

        config.columnconfigure(1, weight=1)

        self.states_entry = self.add_entry(config, "States:", 0)
        self.alphabet_entry = self.add_entry(config, "Alphabet:", 1)
        self.initial_entry = self.add_entry(config, "Initial State:", 2)
        self.finals_entry = self.add_entry(config, "Final States:", 3)

        tk.Label(
            config,
            text="Transitions (source,symbol,destination):",
            font=("Arial", 9, "bold"),
            bg="#f2f4f8"
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(4, 2)
        )

        self.transitions_text = tk.Text(
            config,
            height=4,
            font=("Consolas", 9),
            wrap="none",
            relief="solid",
            borderwidth=1
        )
        self.transitions_text.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=2,
            pady=2
        )

        tk.Button(
            config,
            text="Create / Update Automaton",
            command=self.create_custom_automaton,
            bg="#2878b5",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=3
        ).grid(
            row=6,
            column=0,
            columnspan=2,
            pady=(4, 2)
        )

    def add_entry(self, parent, label, row):

        tk.Label(
            parent,
            text=label,
            font=("Arial", 9, "bold"),
            bg="#f2f4f8"
        ).grid(
            row=row,
            column=0,
            sticky="w",
            pady=2
        )

        entry = tk.Entry(
            parent,
            font=("Arial", 9),
            relief="solid",
            borderwidth=1
        )
        entry.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=5,
            pady=2,
            ipady=2
        )

        return entry

    # ==================================================
    # SIMULATION INTERFACE
    # ==================================================

    def create_simulation(self, parent):

        frame = tk.LabelFrame(
            parent,
            text="String Simulation",
            font=("Arial", 10, "bold"),
            bg="#f2f4f8",
            padx=8,
            pady=5
        )
        frame.pack(fill="both", expand=True, pady=(2, 0))

        frame.columnconfigure(0, weight=1)

        tk.Label(
            frame,
            text="Input String:",
            font=("Arial", 9, "bold"),
            bg="#f2f4f8"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.input_entry = tk.Entry(
            frame,
            font=("Arial", 11),
            relief="solid",
            borderwidth=1
        )
        self.input_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(2, 5),
            ipady=3
        )

        buttons = tk.Frame(frame, bg="#f2f4f8")
        buttons.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=2
        )

        button_data = [
            ("Start", self.start_simulation, "#2878b5"),
            ("Next Step", self.next_step, "#e0a12e"),
            ("Run All", self.run_all, "#16803c"),
            ("Reset", self.reset_simulation, "#64748b")
        ]

        for text, command, color in button_data:
            tk.Button(
                buttons,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 9, "bold"),
                cursor="hand2",
                padx=5,
                pady=4
            ).pack(
                side="left",
                expand=True,
                fill="x",
                padx=2
            )

        info = tk.Frame(frame, bg="#f2f4f8")
        info.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(5, 1)
        )
        info.columnconfigure(0, weight=1)
        info.columnconfigure(1, weight=1)

        symbol_box = tk.Frame(info, bg="#f2f4f8")
        symbol_box.grid(row=0, column=0, sticky="w")

        tk.Label(
            symbol_box,
            text="Current Symbol:",
            font=("Arial", 9, "bold"),
            bg="#f2f4f8"
        ).pack(anchor="w")

        self.symbol_label = tk.Label(
            symbol_box,
            text="-",
            font=("Arial", 12, "bold"),
            bg="#f2f4f8",
            fg="#2878b5"
        )
        self.symbol_label.pack(anchor="w")

        state_box = tk.Frame(info, bg="#f2f4f8")
        state_box.grid(row=0, column=1, sticky="w")

        tk.Label(
            state_box,
            text="Current State(s):",
            font=("Arial", 9, "bold"),
            bg="#f2f4f8"
        ).pack(anchor="w")

        self.current_label = tk.Label(
            state_box,
            text="-",
            font=("Arial", 10, "bold"),
            bg="#f2f4f8",
            fg="#243b53",
            wraplength=250,
            justify="left"
        )
        self.current_label.pack(anchor="w")

        self.progress_label = tk.Label(
            frame,
            text="Progress: 0 / 0",
            font=("Arial", 9),
            bg="#f2f4f8",
            fg="#52677d"
        )
        self.progress_label.grid(
            row=4,
            column=0,
            sticky="w",
            pady=(4, 1)
        )

        self.result_label = tk.Label(
            frame,
            text="Waiting for input",
            font=("Arial", 14, "bold"),
            bg="#f2f4f8",
            fg="#243b53"
        )
        self.result_label.grid(
            row=5,
            column=0,
            pady=3
        )

        tk.Label(
            frame,
            text="Transition Path:",
            font=("Arial", 9, "bold"),
            bg="#f2f4f8"
        ).grid(
            row=6,
            column=0,
            sticky="w",
            pady=(3, 1)
        )

        self.trace_label = tk.Label(
            frame,
            text="No simulation started.",
            font=("Arial", 9),
            bg="#f2f4f8",
            fg="#334e68",
            wraplength=520,
            justify="left",
            anchor="w"
        )
        self.trace_label.grid(
            row=7,
            column=0,
            sticky="ew",
            pady=(1, 3)
        )

    # ==================================================
    # DIAGRAM INTERFACE
    # ==================================================

    def create_diagram(self, parent):

        tk.Label(
            parent,
            text="State Transition Diagram",
            font=("Arial", 13, "bold"),
            bg="#f2f4f8",
            fg="#243b53"
        ).pack(pady=(2, 5))

        self.canvas = tk.Canvas(
            parent,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2
        )

        tk.Label(
            parent,
            text="Green: Visited States and Active Transitions",
            font=("Arial", 9),
            bg="#f2f4f8",
            fg="#16803c"
        ).pack(pady=(4, 2))

        self.canvas.bind("<Configure>", self.on_canvas_resize)

    # ==================================================
    # PRESET AUTOMATA
    # ==================================================

    def load_preset(self, mode):

        self.mode.set(mode)

        if mode == "DFA":

            states = ["q0", "q1", "q2"]
            alphabet = ["0", "1"]
            initial = "q0"
            finals = {"q2"}

            transitions = {
                ("q0", "0"): {"q1"},
                ("q0", "1"): {"q0"},
                ("q1", "0"): {"q1"},
                ("q1", "1"): {"q2"},
                ("q2", "0"): {"q1"},
                ("q2", "1"): {"q0"}
            }

        else:

            states = ["q0", "q1", "q2"]
            alphabet = ["a", "b"]
            initial = "q0"
            finals = {"q2"}

            transitions = {
                ("q0", "a"): {"q0", "q1"},
                ("q0", "b"): {"q0"},
                ("q1", "b"): {"q2"},
                ("q2", "a"): {"q2"},
                ("q2", "b"): {"q2"}
            }

        self.states = states
        self.alphabet = alphabet
        self.initial = initial
        self.finals = finals
        self.transitions = transitions

        self.states_entry.delete(0, tk.END)
        self.states_entry.insert(0, ",".join(states))

        self.alphabet_entry.delete(0, tk.END)
        self.alphabet_entry.insert(0, ",".join(alphabet))

        self.initial_entry.delete(0, tk.END)
        self.initial_entry.insert(0, initial)

        self.finals_entry.delete(0, tk.END)
        self.finals_entry.insert(0, ",".join(sorted(finals)))

        self.transitions_text.delete("1.0", tk.END)

        lines = []
        for (source, symbol), destinations in transitions.items():
            for destination in sorted(destinations):
                lines.append(f"{source},{symbol},{destination}")

        self.transitions_text.insert("1.0", "\n".join(lines))

        self.reset_simulation()
        self.draw_diagram()

    # ==================================================
    # CUSTOM AUTOMATON CREATION
    # ==================================================

    def create_custom_automaton(self):

        try:

            states = [
                x.strip()
                for x in self.states_entry.get().split(",")
                if x.strip()
            ]

            alphabet = [
                x.strip()
                for x in self.alphabet_entry.get().split(",")
                if x.strip()
            ]

            initial = self.initial_entry.get().strip()

            finals = {
                x.strip()
                for x in self.finals_entry.get().split(",")
                if x.strip()
            }

            if not states or not alphabet:
                raise ValueError("States and alphabet cannot be empty.")

            if len(states) != len(set(states)):
                raise ValueError("Duplicate state names are not allowed.")

            if len(alphabet) != len(set(alphabet)):
                raise ValueError("Duplicate alphabet symbols are not allowed.")

            if any(len(symbol) != 1 for symbol in alphabet):
                raise ValueError("Each alphabet symbol must be one character.")

            if initial not in states:
                raise ValueError("Initial state must be in the states list.")

            if not finals or not finals.issubset(set(states)):
                raise ValueError("Final states must be in the states list.")

            transitions = {}

            lines = self.transitions_text.get("1.0", tk.END).strip().splitlines()

            for line in lines:

                if not line.strip():
                    continue

                parts = [x.strip() for x in line.split(",")]

                if len(parts) != 3:
                    raise ValueError(
                        "Use this transition format:\n"
                        "source,symbol,destination"
                    )

                source, symbol, destination = parts

                if source not in states:
                    raise ValueError(f"Unknown source state: {source}")

                if destination not in states:
                    raise ValueError(f"Unknown destination state: {destination}")

                if symbol not in alphabet:
                    raise ValueError(f"Unknown alphabet symbol: {symbol}")

                transitions.setdefault((source, symbol), set()).add(destination)

            if self.mode.get() == "DFA":

                for state in states:
                    for symbol in alphabet:

                        destinations = transitions.get((state, symbol), set())

                        if len(destinations) != 1:
                            raise ValueError(
                                "DFA requires exactly one destination "
                                f"for {state} with symbol {symbol}."
                            )

            self.states = states
            self.alphabet = alphabet
            self.initial = initial
            self.finals = finals
            self.transitions = transitions

            self.reset_simulation()
            self.draw_diagram()

            messagebox.showinfo(
                "Success",
                "Automaton created successfully!"
            )

        except ValueError as error:
            messagebox.showerror("Configuration Error", str(error))

    # ==================================================
    # START SIMULATION
    # ==================================================

    def start_simulation(self):

        word = self.input_entry.get()

        if not self.states or not self.initial:
            messagebox.showerror(
                "Error",
                "Please create an automaton first."
            )
            return

        invalid = [
            symbol for symbol in word
            if symbol not in self.alphabet
        ]

        if invalid:
            messagebox.showerror(
                "Invalid Input",
                "The input contains symbols outside the alphabet: "
                + ", ".join(sorted(set(invalid)))
            )
            return

        self.word = word
        self.position = 0

        self.current_states = {self.initial}
        self.visited_states = {self.initial}
        self.active_edges = set()

        self.path = [
            "{" + self.initial + "}"
            if self.mode.get() == "NFA"
            else self.initial
        ]

        self.simulation_started = True
        self.simulation_finished = False

        self.result_label.config(
            text="SIMULATION IN PROGRESS",
            fg="#2878b5"
        )

        self.symbol_label.config(text="-")

        self.update_simulation_display()
        self.draw_diagram()

        if len(self.word) == 0:
            self.finish_simulation()

    # ==================================================
    # PROCESS ONE SYMBOL
    # ==================================================

    def next_step(self):

        if not self.simulation_started:
            messagebox.showwarning(
                "Start First",
                "Please press Start before Next Step."
            )
            return

        if self.simulation_finished:
            return

        if self.position >= len(self.word):
            self.finish_simulation()
            return

        symbol = self.word[self.position]
        next_states = set()

        if self.mode.get() == "DFA":

            if self.current_states:

                state = next(iter(self.current_states))

                destinations = self.transitions.get(
                    (state, symbol), set()
                )

                if len(destinations) == 1:

                    destination = next(iter(destinations))

                    self.active_edges.add(
                        (state, symbol, destination)
                    )
                    next_states.add(destination)

        else:

            for state in self.current_states:

                destinations = self.transitions.get(
                    (state, symbol), set()
                )

                for destination in destinations:

                    self.active_edges.add(
                        (state, symbol, destination)
                    )
                    next_states.add(destination)

        self.current_states = next_states
        self.visited_states.update(next_states)
        self.position += 1

        if self.mode.get() == "NFA":

            current_text = (
                "{"
                + ", ".join(sorted(self.current_states))
                + "}"
            )

        else:

            current_text = (
                next(iter(self.current_states))
                if self.current_states
                else "No active state"
            )

        self.path.append(current_text)

        self.symbol_label.config(text=symbol)

        self.update_simulation_display()
        self.draw_diagram()

        if self.position >= len(self.word):
            self.finish_simulation()

    # ==================================================
    # RUN ALL
    # ==================================================

    def run_all(self):

        if not self.simulation_started:
            self.start_simulation()

        if not self.simulation_started:
            return

        while not self.simulation_finished:
            self.next_step()

    # ==================================================
    # FINISH SIMULATION
    # ==================================================

    def finish_simulation(self):

        self.simulation_finished = True

        accepted = bool(
            self.current_states.intersection(self.finals)
        )

        if accepted:
            self.result_label.config(
                text="ACCEPTED",
                fg="#16803c"
            )
        else:
            self.result_label.config(
                text="REJECTED",
                fg="#dc2626"
            )

        self.symbol_label.config(text="Completed")

        self.update_simulation_display()
        self.draw_diagram()

    # ==================================================
    # UPDATE DISPLAY
    # ==================================================

    def update_simulation_display(self):

        if self.mode.get() == "NFA":

            current_text = (
                "{"
                + ", ".join(sorted(self.current_states))
                + "}"
            )

        else:

            current_text = (
                next(iter(self.current_states))
                if self.current_states
                else "No active state"
            )

        self.current_label.config(text=current_text)

        self.progress_label.config(
            text=f"Progress: {self.position} / {len(self.word)}"
        )

        self.trace_label.config(
            text=" -> ".join(self.path)
        )

    # ==================================================
    # RESET
    # ==================================================

    def reset_simulation(self):

        self.word = ""
        self.position = 0

        self.current_states = set()
        self.visited_states = set()
        self.active_edges = set()
        self.path = []

        self.simulation_started = False
        self.simulation_finished = False

        if hasattr(self, "symbol_label"):

            self.symbol_label.config(text="-")
            self.current_label.config(text="-")
            self.progress_label.config(text="Progress: 0 / 0")

            self.result_label.config(
                text="Waiting for input",
                fg="#243b53"
            )

            self.trace_label.config(text="No simulation started.")

        self.draw_diagram()

    # ==================================================
    # DRAW DIAGRAM
    # ==================================================

    def on_canvas_resize(self, event):
        self.draw_diagram()

    def draw_diagram(self):

        if not hasattr(self, "canvas"):
            return

        self.canvas.delete("all")

        if not self.states or self.initial not in self.states:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 100 or height < 100:
            return

        center_x = width / 2
        center_y = height / 2

        count = len(self.states)
        positions = {}

        if count <= 3:

            if count == 1:
                spacing = 0
            else:
                spacing = min(
                    (width - 220) / (count - 1),
                    220
                )

            spacing = max(spacing, 125)

            for i, state in enumerate(self.states):

                x = center_x + (
                    i - (count - 1) / 2
                ) * spacing

                positions[state] = (x, center_y)

        else:

            radius = min(
                width * 0.34,
                height * 0.32,
                230
            )

            for i, state in enumerate(self.states):

                angle = (
                    -math.pi / 2
                    + 2 * math.pi * i / count
                )

                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)

                positions[state] = (x, y)

        # Initial arrow

        ix, iy = positions[self.initial]

        self.canvas.create_line(
            ix - 95,
            iy,
            ix - 42,
            iy,
            arrow=tk.LAST,
            width=2,
            fill="#245b83"
        )

        # Group transitions

        edges = {}

        for (source, symbol), destinations in self.transitions.items():

            for destination in destinations:

                edges.setdefault(
                    (source, destination), []
                ).append(symbol)

        state_index = {
            state: i
            for i, state in enumerate(self.states)
        }

        # Draw transitions

        for (source, destination), symbols in edges.items():

            if source not in positions or destination not in positions:
                continue

            x1, y1 = positions[source]
            x2, y2 = positions[destination]

            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)

            # Self-loop

            if source == destination:

                active = any(
                    (source, symbol, destination) in self.active_edges
                    for symbol in symbols
                )

                color = "#16a34a" if active else "#245b83"
                line_width = 4 if active else 2

                self.canvas.create_line(
                    x1 - 20, y1 - 28,
                    x1 - 55, y1 - 85,
                    x1, y1 - 110,
                    x1 + 55, y1 - 85,
                    x1 + 20, y1 - 28,
                    smooth=True,
                    arrow=tk.LAST,
                    width=line_width,
                    fill=color
                )

                self.create_label(
                    x1,
                    y1 - 112,
                    ", ".join(sorted(symbols)),
                    color
                )

                continue

            if length == 0:
                continue

            ux = dx / length
            uy = dy / length

            start_x = x1 + ux * 39
            start_y = y1 + uy * 39

            end_x = x2 - ux * 39
            end_y = y2 - uy * 39

            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2

            perp_x = -uy
            perp_y = ux

            curve = 0

            if count <= 3:

                source_i = state_index[source]
                destination_i = state_index[destination]
                difference = destination_i - source_i

                if abs(difference) == 1:

                    reverse_exists = (
                        destination,
                        source
                    ) in edges

                    if reverse_exists and difference < 0:
                        curve = 90

                elif abs(difference) > 1:

                    if difference < 0:
                        curve = -150
                    else:
                        curve = 150

            control_x = mid_x + perp_x * curve
            control_y = mid_y + perp_y * curve

            active = any(
                (source, symbol, destination) in self.active_edges
                for symbol in symbols
            )

            color = "#16a34a" if active else "#245b83"
            line_width = 4 if active else 2

            self.canvas.create_line(
                start_x,
                start_y,
                control_x,
                control_y,
                end_x,
                end_y,
                smooth=True,
                arrow=tk.LAST,
                width=line_width,
                fill=color
            )

            label = ", ".join(sorted(symbols))

            if curve == 0:
                label_x = mid_x
                label_y = mid_y - 19
            else:
                label_x = control_x + perp_x * 12
                label_y = control_y + perp_y * 12

            self.create_label(
                label_x,
                label_y,
                label,
                color
            )

        # Draw states last

        for state, (x, y) in positions.items():

            visited = state in self.visited_states
            current = state in self.current_states

            if current:
                fill = "#a7e9bb"
                outline = "#087c37"

            elif visited:
                fill = "#d0f2da"
                outline = "#16803c"

            else:
                fill = "#dceeff"
                outline = "#245b83"

            self.canvas.create_oval(
                x - 36,
                y - 36,
                x + 36,
                y + 36,
                fill=fill,
                outline=outline,
                width=3
            )

            # Final state double circle

            if state in self.finals:

                self.canvas.create_oval(
                    x - 29,
                    y - 29,
                    x + 29,
                    y + 29,
                    outline=outline,
                    width=2
                )

            self.canvas.create_text(
                x,
                y,
                text=state,
                font=("Arial", 11, "bold"),
                fill="#183b56"
            )

    # ==================================================
    # DRAW LABEL WITH BACKGROUND
    # ==================================================

    def create_label(self, x, y, text, color):

        text_id = self.canvas.create_text(
            x,
            y,
            text=text,
            fill=color,
            font=("Arial", 11, "bold"),
            justify="center"
        )

        bbox = self.canvas.bbox(text_id)

        if bbox:

            x1, y1, x2, y2 = bbox

            bg_id = self.canvas.create_rectangle(
                x1 - 4,
                y1 - 3,
                x2 + 4,
                y2 + 3,
                fill="white",
                outline="white"
            )

            self.canvas.tag_lower(bg_id, text_id)


# ======================================================
# RUN APPLICATION
# ======================================================

if __name__ == "__main__":

    root = tk.Tk()
    app = AutomataSimulator(root)
    root.mainloop()