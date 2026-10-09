(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.0abfcec96d82e3bf.js","sha256":"0abfcec96d82e3bfba5a99576ab30b4b170fe348dd818f1534ba7864db8bb6a9","count":244});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
