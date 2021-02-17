document.addEventListener("DOMContentLoaded", () => {

    const overlayElem: HTMLElement = document.getElementById("overlay");

    const modalPlayer: HTMLElement = document.getElementById("modalPlayer");
    const modalPlayerButton: Element = modalPlayer.getElementsByClassName("form__button")[0];
    const modalOpeningAnimationClass: string = "modal--opening";
    const modalClosingAnimationClass: string = "modal--closing";


    let xTouchDown: number | null = null;
    let yTouchDown: number | null = null;

    //=== Handle touch start
    function handleTouchStart(evt: any) {
        xTouchDown = evt.touches[0].clientX;
        yTouchDown = evt.touches[0].clientY;
    };          
    
    //=== Handle touch swipe
    function handleTouchMove(evt: any) {
        if (!xTouchDown || !yTouchDown)
            return;
        
        const xTouchUp = evt.touches[0].clientX; 
        const yTouchUp = evt.touches[0].clientY;
        
        let xDiff = xTouchDown - xTouchUp;
        let yDiff = yTouchDown - yTouchUp;

        if (Math.abs(xDiff) > Math.abs(yDiff)) {
            if (xDiff > 0) {
                /* left swipe */ 
            } else {
                /* right swipe */
            }
        } else {
            if (yDiff > 0) {
                /* up swipe */ 
            } else { 
                /* down swipe */
                handleModalClosing(modalPlayer);
            }                                                                 
        }
        
        xTouchDown = null;
        yTouchDown = null;                                             
    };


    //=== Check if event came from modal
    function isTargetModal(target: HTMLElement): boolean {
        let isFromModal = false;
        let elems: HTMLElement[] = [];

        while (!isFromModal && target.classList.length > 0) {
            if (target.classList.contains('modal')) {
                isFromModal = true;
            }

            elems.unshift(target);
            target = target.parentNode as HTMLElement;
        }
        return isFromModal;
    }


    function handleModalClosing(modalElem: HTMLElement): void {
        const animationDuration = window.getComputedStyle(document.documentElement).getPropertyValue('--animation-global-duration');
        const animationDurationSecond = parseFloat(animationDuration.replace(/\D+$/g, '')); //=== Remove s from duration

        if (modalElem.classList.contains(modalOpeningAnimationClass)) {
            modalElem.classList.add(modalClosingAnimationClass)
            modalElem.classList.remove(modalOpeningAnimationClass);
        }

        /* Hide after animation end */
        setTimeout(() => {
            if (!overlayElem.classList.contains('hidden'))
                overlayElem.classList.add('hidden')

            modalElem.classList.add('hidden');
        }, animationDurationSecond * 1000);
    }


    function handlePlayerModal(event: any): void {
        event.stopPropagation();
        handleModalClosing(modalPlayer);
    }

    function handleModalOpening(modalElem: HTMLElement) : void {

       console.info('POpening modal player');
        modalElem.classList.remove('hidden');

        if (overlayElem.classList.contains('hidden'))
            overlayElem.classList.remove('hidden')

        if (!modalElem.classList.contains(modalOpeningAnimationClass)) {
            modalElem.classList.remove(modalClosingAnimationClass)
            modalElem.classList.add(modalOpeningAnimationClass);
        }
    }

    //=== Event binding
    console.info('It should open the model');
    handleModalOpening(modalPlayer);
    modalPlayerButton.addEventListener("click",handlePlayerModal);


});