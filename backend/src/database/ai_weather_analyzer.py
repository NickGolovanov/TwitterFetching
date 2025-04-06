import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer


class WeatherAnalyzer:
    def __init__(self, model_name="xlm-roberta-base"):
        """
        Initialize a weather analyzer using RoBERTa model for multilingual
        weather analysis.
        """

        print(f"Loading model {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(
            model_name, torch_dtype=torch.float16
        )

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        # Weather type categories and their danger level to property (0-10 scale)
        # English weather types
        self.weather_types_en = {
            "thunderstorm": 9,
            "thunder": 8,
            "hurricane": 10,
            "tornado": 10,
            "typhoon": 10,
            "cyclone": 10,
            "hail": 8,
            "flood": 9,
            "flash flood": 9,
            "wildfire": 10,
            "blizzard": 7,
            "heavy snow": 6,
            "ice storm": 8,
            "freezing rain": 7,
            "heavy rain": 5,
            "strong wind": 6,
            "high wind": 7,
            "dust storm": 6,
            "sandstorm": 6,
            "fog": 3,
            "heat wave": 4,
            "drought": 5,
            "frost": 4,
            "cold wave": 5,
            "rain": 3,
            "snow": 4,
            "wind": 3,
            "cloudy": 1,
            "overcast": 1,
            "partly cloudy": 1,
            "sunny": 1,
            "clear": 1,
            "fair": 1,
            "mild": 1,
            "warm": 1,
            "drizzle": 2,
            "mist": 2,
            "light rain": 2,
        }

        # Dutch weather types
        self.weather_types_nl = {
            "onweer": 9,
            "donder": 8,
            "orkaan": 10,
            "tornado": 10,
            "tyfoon": 10,
            "cycloon": 10,
            "hagel": 8,
            "overstroming": 9,
            "wolkbreuk": 9,
            "bosbrand": 10,
            "sneeuwstorm": 7,
            "zware sneeuw": 6,
            "ijsstorm": 8,
            "ijsregen": 7,
            "zware regen": 5,
            "harde wind": 6,
            "stormachtig": 7,
            "zandstorm": 6,
            "mist": 3,
            "hittegolf": 4,
            "droogte": 5,
            "vorst": 4,
            "koudegolf": 5,
            "regen": 3,
            "sneeuw": 4,
            "wind": 3,
            "bewolkt": 1,
            "betrokken": 1,
            "halfbewolkt": 1,
            "zonnig": 1,
            "helder": 1,
            "mooi weer": 1,
            "mild": 1,
            "warm": 1,
            "motregen": 2,
            "nevel": 2,
            "lichte regen": 2,
        }

        self.weather_types = {**self.weather_types_en, **self.weather_types_nl}

        # Severity modifiers in English
        self.severity_modifiers_en = {
            # Intensifiers
            "severe": 2,
            "extreme": 3,
            "dangerous": 2,
            "heavy": 1.5,
            "strong": 1.5,
            "intense": 1.5,
            "violent": 2,
            "devastating": 2.5,
            "destructive": 2,
            "damaging": 1.5,
            "catastrophic": 3,
            # Property damage terms
            "damage": 1.5,
            "property damage": 2,
            "roof damage": 2,
            "structural damage": 2.5,
            "destroyed": 3,
            "broken windows": 1.5,
            "flooding": 2,
            "power outage": 1.5,
            "downed trees": 1.5,
            "downed power lines": 2,
            # Diminishers
            "light": -1,
            "mild": -1.5,
            "slight": -1,
            "brief": -0.5,
            "passing": -1,
            "scattered": -0.5,
            "isolated": -1,
            "ending": -1,
            "clearing": -1,
            "improving": -1,
        }

        # Severity modifiers in Dutch
        self.severity_modifiers_nl = {
            # Intensifiers
            "ernstig": 2,
            "extreem": 3,
            "gevaarlijk": 2,
            "zwaar": 1.5,
            "sterk": 1.5,
            "intens": 1.5,
            "gewelddadig": 2,
            "verwoestend": 2.5,
            "destructief": 2,
            "beschadigend": 1.5,
            "catastrofaal": 3,
            # Property damage terms
            "schade": 1.5,
            "materiële schade": 2,
            "dakschade": 2,
            "structurele schade": 2.5,
            "verwoest": 3,
            "gebroken ruiten": 1.5,
            "overstroming": 2,
            "stroomuitval": 1.5,
            "omgevallen bomen": 1.5,
            "omgevallen hoogspanningsmasten": 2,
            # Diminishers
            "licht": -1,
            "mild": -1.5,
            "geringe": -1,
            "kort": -0.5,
            "voorbijgaand": -1,
            "verspreid": -0.5,
            "geïsoleerd": -1,
            "afnemend": -1,
            "opklarend": -1,
            "verbeterend": -1,
        }

        # Combined modifiers
        self.severity_modifiers = {
            **self.severity_modifiers_en,
            **self.severity_modifiers_nl,
        }

        print("Model loaded successfully. Ready for analysis.")

    def analyze_weather_text(self, text, max_length=280):
        """
        Analyze text to determine weather type and severity based on context.
        Works for both English and Dutch.
        """
        if len(text) > max_length:
            text = text[:max_length]

        text_lower = text.lower()

        found_weather_types = []
        for weather_type in self.weather_types.keys():
            if weather_type in text_lower:
                found_weather_types.append(weather_type)

        if not found_weather_types:
            found_weather_types = self._infer_weather_type(text)

        if not found_weather_types:
            return {
                "weather_type": "unknown",
                "severity_score": 0,
                "severity_category": "unknown",
                "explanation": "No weather condition detected in the text.",
            }

        primary_weather_type = max(
            found_weather_types, key=lambda x: self.weather_types[x]
        )
        base_severity = self.weather_types[primary_weather_type]

        severity_adjustment = 0
        applied_modifiers = []

        for modifier, value in self.severity_modifiers.items():
            if modifier in text_lower:
                if value > 0:
                    for weather_term in found_weather_types:
                        if self._terms_are_close(
                            text_lower, modifier, weather_term, max_distance=5
                        ):
                            severity_adjustment += value
                            applied_modifiers.append(f"+{value} ({modifier})")
                            break
                        elif modifier not in [
                            item.split("(")[1].split(")")[0]
                            for item in applied_modifiers
                        ]:
                            severity_adjustment += value / 2
                            applied_modifiers.append(
                                f"+{value/2} ({modifier}, not directly associated)"
                            )
                else:
                    for weather_term in found_weather_types:
                        if self._terms_are_close(
                            text_lower, modifier, weather_term, max_distance=5
                        ):
                            severity_adjustment += value  # value is negative
                            applied_modifiers.append(f"{value} ({modifier})")
                            break
                        elif modifier not in [
                            item.split("(")[1].split(")")[0]
                            for item in applied_modifiers
                        ]:
                            severity_adjustment += value / 2
                            applied_modifiers.append(
                                f"{value/2} ({modifier}, not directly associated)"
                            )

        context_adjustment = self._assess_contextual_severity(
            text, primary_weather_type
        )
        if context_adjustment != 0:
            severity_adjustment += context_adjustment
            applied_modifiers.append(
                f"{context_adjustment:+.1f} (contextual assessment)"
            )

        # Calculate final severity score (0-10 scale)
        final_severity = max(0, min(10, base_severity + severity_adjustment))

        # Map to severity category
        severity_category = self._get_severity_category(final_severity)

        # Prepare explanation for the user
        if applied_modifiers:
            explanation = (
                f"Base severity for {primary_weather_type}: {base_severity}/10\n"
            )
            explanation += "Modifiers applied: " + ", ".join(applied_modifiers) + "\n"
            explanation += f"Final severity score: {final_severity:.1f}/10"
        else:
            explanation = f"Weather type '{primary_weather_type}' has a standard severity of {base_severity}/10 for potential property damage."

        # Detect language
        language = (
            "dutch"
            if any(term in self.weather_types_nl for term in found_weather_types)
            else "english"
        )

        return {
            "weather_type": primary_weather_type,
            "all_detected_types": found_weather_types,
            "severity_score": round(final_severity, 1),
            "severity_category": severity_category,
            "language": language,
            "explanation": explanation,
        }

    def _terms_are_close(self, text, term1, term2, max_distance=5):
        """Check if two terms appear close to each other in text"""
        words = text.split()

        # Find positions of both terms
        positions1 = [i for i, word in enumerate(words) if term1 in word]
        positions2 = [i for i, word in enumerate(words) if term2 in word]

        # Check if any pair of positions is close enough
        for pos1 in positions1:
            for pos2 in positions2:
                if abs(pos1 - pos2) <= max_distance:
                    return True
        return False

    def _infer_weather_type(self, text):
        """Use RoBERTa to infer weather type when not explicitly mentioned"""
        # Create templates to fill in with masked tokens
        mask_token = self.tokenizer.mask_token
        templates = [
            f"If this describes weather, the weather type is {mask_token}, otherwise it's not weather-related: {text}",
            f"Looking only for weather conditions in the text: '{text}', the weather type is {mask_token}, or none if not about weather",
            f"The weather phenomenon in this text is {mask_token}, or none if no weather is mentioned: {text}",
        ]

        weather_scores = {}

        for template in templates:
            # Tokenize the input
            inputs = self.tokenizer(template, return_tensors="pt").to(self.device)

            # Find position of [MASK]
            mask_token_index = torch.where(
                inputs["input_ids"] == self.tokenizer.mask_token_id
            )[1]

            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = outputs.logits[0, mask_token_index, :]

            # Get top predictions
            top_tokens = (
                torch.topk(predictions, k=5, dim=1).indices[0].tolist()
            )  # Reduced from 20 to 5
            top_words = [
                self.tokenizer.decode([token]).lower().strip() for token in top_tokens
            ]

            # Match with our weather types and accumulate scores
            for i, word in enumerate(top_words):
                score = 1.0 / (i + 1)  # Higher rank gets higher score
                if word in [
                    "none",
                    "no",
                    "not",
                    "nothing",
                ]:  # Skip if model suggests no weather
                    continue
                for weather_type in self.weather_types.keys():
                    if word == weather_type:  # Only exact matches
                        if weather_type in weather_scores:
                            weather_scores[weather_type] += score
                        else:
                            weather_scores[weather_type] = score

        # Return the top matched weather types, if any
        if weather_scores:
            sorted_types = sorted(
                weather_scores.items(), key=lambda x: x[1], reverse=True
            )
            return [sorted_types[0][0]]  # Return the highest scoring weather type
        return []

    def _assess_contextual_severity(self, text, weather_type):
        """
        Use RoBERTa to assess contextual severity beyond explicit modifiers
        Returns a severity adjustment value
        """

        mask_token = self.tokenizer.mask_token
        templates = [
            f"The {weather_type} described in '{text}' is {mask_token} severe.",
            f"The severity of the {weather_type} in '{text}' can be described as {mask_token}.",
        ]

        # Severity assessment mapping
        severity_mapping = {
            "extremely": 2.0,
            "very": 1.5,
            "quite": 1.0,
            "unusually": 1.0,
            "highly": 1.5,
            "exceptionally": 2.0,
            "remarkably": 1.5,
            "notably": 1.0,
            "particularly": 1.0,
            "especially": 1.5,
            "dangerously": 2.0,
            "not": -1.5,
            "less": -1.0,
            "somewhat": 0.5,
            "moderately": 0.0,
            "mildly": -0.5,
            "barely": -1.5,
            "hardly": -1.5,
            "slightly": -1.0,
            "minimally": -1.5,
            "rarely": -1.0,
            "seldom": -1.0,
            "insignificantly": -1.5,
            "neglibly": -2.0,
            "typically": 0.0,
        }

        severity_scores = {}

        for template in templates:
            # Tokenize the input
            inputs = self.tokenizer(template, return_tensors="pt").to(self.device)

            # Find position of [MASK]
            mask_token_index = torch.where(
                inputs["input_ids"] == self.tokenizer.mask_token_id
            )[1]

            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = outputs.logits[0, mask_token_index, :]

            # Get top predictions
            top_tokens = torch.topk(predictions, k=10, dim=1).indices[0].tolist()
            top_words = [
                self.tokenizer.decode([token]).lower().strip() for token in top_tokens
            ]

            # Match with severity mapping and accumulate scores
            for i, word in enumerate(top_words):
                score = 1.0 / (i + 1)  # Higher rank gets higher score
                for severity_word, adjustment in severity_mapping.items():
                    if severity_word == word or severity_word in word:
                        if severity_word in severity_scores:
                            severity_scores[severity_word] += score
                        else:
                            severity_scores[severity_word] = score

        # Calculate weighted average of severity adjustments
        if severity_scores:
            total_score = sum(severity_scores.values())
            weighted_adjustment = (
                sum(
                    severity_scores[word] * severity_mapping[word]
                    for word in severity_scores
                )
                / total_score
            )
            return weighted_adjustment

        return 0  # Default if no adjustment found

    def _get_severity_category(self, score):
        """Converts a numerical severity score to a category"""
        if score >= 8:
            return "extreme"
        elif score >= 6:
            return "high"
        elif score >= 3:
            return "moderate"
        elif score > 0:
            return "low"
        else:
            return "unknown"
