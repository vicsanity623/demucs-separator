module.exports = {
  version: "1.0",
  title: "2D Schematic Simulator",
  description: "My Pinokio App",
  menu: async (kernel) => {
    // Check if the "env" folder exists to see if it's installed
    let installed = await kernel.exists(__dirname, "env")
    
    if (installed) {
      return [
        {
          icon: "fa-solid fa-power-off",
          text: "Start",
          href: "start.json",
        },
        {
          icon: "fa-solid fa-plug",
          text: "Update / Reinstall",
          href: "install.json",
        }
      ]
    } else {
      return [
        {
          icon: "fa-solid fa-plug",
          text: "Install",
          href: "install.json",
        }
      ]
    }
  }
}