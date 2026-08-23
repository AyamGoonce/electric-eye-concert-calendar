(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.146f46b33dada418.js","sha256":"146f46b33dada41819f56860c7c8b9bc79954e7e7a72454e84f60322409bd030","count":1741,"publishedAt":"2026-08-23T16:46:51Z","state":"calendar-state.json","stateSha256":"8fd3112ffe68833fe77a8a7ff0808adbf3d6ee1ba7bee1d1f9d4a2d82a5d69f7"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
